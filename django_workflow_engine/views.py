import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict, cast

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.http.response import Http404, HttpResponse, HttpResponseBase, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView

from django_workflow_engine import COMPLETE
from django_workflow_engine.dataclass import Step
from django_workflow_engine.exceptions import WorkflowNotAuthError
from django_workflow_engine.executor import WorkflowExecutor
from django_workflow_engine.models import Flow, TaskStatus
from django_workflow_engine.tasks import TaskError
from django_workflow_engine.utils import build_workflow_choices

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from django.contrib.auth.models import User
else:
    User = get_user_model()


class FlowListView(ListView):
    model = Flow
    paginate_by = 100  # if pagination is desired
    ordering = "-started"


class FlowView(DetailView):
    model = Flow


class FlowCreateForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["workflow_name"] = forms.ChoiceField(
            choices=build_workflow_choices(settings.DJANGO_WORKFLOWS)
        )

    class Meta:
        model = Flow
        fields = ["workflow_name", "flow_name", "executed_by"]
        widgets = {
            "executed_by": forms.HiddenInput,
        }


class FlowCreateView(CreateView):
    model = Flow
    form_class = FlowCreateForm

    def get_success_url(self) -> str:
        assert self.object

        return reverse("flow", args=[self.object.pk])

    def get_initial(self):
        return {
            "executed_by": self.request.user,
        }

    def form_valid(self, form) -> HttpResponse:
        user = cast(User, self.request.user)
        response = super().form_valid(form)

        assert self.object

        self.object.executed_by = user
        self.object.save()

        executor = WorkflowExecutor(self.object)
        try:
            executor.run_flow(user=user)
        except WorkflowNotAuthError as e:
            logger.warning(f"{e}")
            raise PermissionDenied(f"{e}")

        return response


class FlowDeleteView(DeleteView):
    model = Flow
    success_url = reverse_lazy("flow-list")


class FlowContinueView(TemplateView):
    template_name = "django_workflow_engine/flow-continue.html"
    cannot_view_step_url = None

    flow: Flow
    authorised_next_steps: List[Step] = []
    workflow_executor: WorkflowExecutor

    def get_cannot_view_step_url(self) -> str:
        return reverse(
            "flow",
            args=[self.flow.pk],
        )

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().setup(request, *args, **kwargs)

        self.flow: Flow = get_object_or_404(Flow, pk=kwargs["pk"])
        self.workflow_executor = WorkflowExecutor(self.flow)
        next_steps: List[Step] = self.workflow_executor.get_current_steps()
        self.authorised_next_steps: List[Step] = []

        if request.user.is_authenticated:
            # Build a list of the next steps that the user is authorised to action.
            for next_step in next_steps:
                try:
                    self.workflow_executor.check_authorised(
                        request.user,
                        next_step,
                    )
                except WorkflowNotAuthError:
                    # User not authorised, skip this step
                    continue

                self.authorised_next_steps.append(next_step)

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        if not self.authorised_next_steps:
            return redirect(self.get_cannot_view_step_url())
        return super().dispatch(request, *args, **kwargs)

    def get_step(self, step_id: str) -> Optional[Step]:
        for step in self.authorised_next_steps:
            if step.step_id == step_id:
                return step
        return None

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        user = cast(User, request.user)

        step_id = request.POST.get("step_id", None)
        if not step_id:
            return redirect("flow-continue", pk=self.flow.pk)

        step: Optional[Step] = self.get_step(step_id=step_id)
        if not step:
            return redirect("flow-continue", pk=self.flow.pk)

        try:
            self.workflow_executor.execute_step(
                user=user,
                step=step,
            )
        except WorkflowNotAuthError as e:
            logger.warning(f"{e}")
            raise PermissionDenied(f"{e}")
        except TaskError as error:
            context = self.get_context_data() | error.context
            return super().render_to_response(context=context)
        return redirect(reverse("flow", args=[self.flow.pk]))

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            flow=self.flow,
            authorised_next_steps=self.authorised_next_steps,
        )
        return context


class FlowDiagramView(View):
    def get(
        self, request: HttpRequest, pk: int, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        try:
            flow: Flow = Flow.objects.get(pk=pk)
        except Flow.DoesNotExist:
            raise Http404(f"Flow {pk} not found")
        elements = workflow_to_cytoscape_elements(flow)
        return JsonResponse({"elements": elements})


class Node(TypedDict):
    id: str
    label: str
    start: bool
    end: bool
    decision: bool
    done: bool
    current: bool


class NodeData(TypedDict):
    data: Node


class Edge(TypedDict):
    id: str
    source: str
    target: str


class EdgeData(TypedDict):
    data: Edge


def workflow_to_cytoscape_elements(flow: Flow):
    nodes: List[NodeData] = [
        {
            "data": step_to_node(flow, step),
        }
        for step in flow.workflow.steps
    ]

    edges: List[EdgeData] = [
        {
            "data": {
                "id": f"{step.step_id}{target}",
                "source": step.step_id,
                "target": target,
            }
        }
        for step in flow.workflow.steps
        if step.targets != COMPLETE
        for target in step.targets
        if target
    ]

    return {"nodes": nodes, "edges": edges}


def step_to_node(flow: Flow, step: Step) -> Node:
    latest_step_task: Optional[TaskStatus] = (
        flow.tasks.order_by("started_at").filter(step_id=step.step_id).last()
    )

    targets = step.targets

    end = not bool(targets)
    done = bool(latest_step_task and latest_step_task.done)
    current = bool(latest_step_task and not latest_step_task.executed_at)

    label = step.description or format_step_id(step.step_id)
    if end and done:
        label += " ✓"

    return {
        "id": step.step_id,
        "label": label,
        "start": bool(step.start),
        "end": end,
        "decision": len(targets) > 1,
        "done": done,
        "current": current,
    }


def format_step_id(step_id: str) -> str:
    # email_all_users -> Email all users
    return step_id.replace("_", " ").title()
