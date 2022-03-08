import logging
from typing import List, Optional

from django import forms
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView

from django_workflow_engine.dataclass import Step
from django_workflow_engine.exceptions import WorkflowNotAuthError
from django_workflow_engine.executor import WorkflowExecutor
from django_workflow_engine.models import Flow, TaskRecord
from django_workflow_engine.tasks import TaskError
from django_workflow_engine.utils import build_workflow_choices

logger = logging.getLogger(__name__)


class FlowListView(ListView):
    model = Flow
    paginate_by = 100  # if pagination is desired
    ordering = "-started"


class FlowView(DetailView):
    model = Flow


class FlowCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["workflow_name"] = forms.ChoiceField(
            choices=build_workflow_choices(settings.DJANGO_WORKFLOWS)
        )

    class Meta:
        model = Flow
        fields = ["workflow_name", "flow_name"]


class FlowCreateView(CreateView):
    model = Flow
    form_class = FlowCreateForm

    def get_success_url(self):
        return reverse("flow", args=[self.object.pk])

    def form_valid(self, form):
        response = super().form_valid(form)

        self.object.executed_by = self.request.user
        self.object.save()

        executor = WorkflowExecutor(self.object)
        try:
            executor.run_flow(user=self.request.user)
        except WorkflowNotAuthError as e:
            logger.warning(f"{e}")
            raise PermissionDenied(f"{e}")

        return response


class FlowDeleteView(DeleteView):
    model = Flow
    success_url = reverse_lazy("flow-list")


from django.views.generic import TemplateView


class FlowContinueView(TemplateView):
    template_name = "django_workflow_engine/flow-continue.html"
    cannot_view_step_url = None

    flow: Flow
    authorised_next_steps: List[Step] = []
    workflow_executor: WorkflowExecutor

    def get_cannot_view_step_url(self):
        return reverse_lazy(
            "flow",
            args=[self.flow.pk],
        )

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.flow: Flow = Flow.objects.get(pk=kwargs.get("pk"))
        self.workflow_executor = WorkflowExecutor(self.flow)
        next_steps: List[Step] = self.workflow_executor.get_current_steps()
        self.authorised_next_steps: List[Step] = []

        # Build a list of the next steps that the user is authorised to action.
        for next_step in next_steps:
            try:
                self.workflow_executor.check_authorised(
                    request.user,
                    self.step,
                )
            except WorkflowNotAuthError:
                # User not authorised, skip this step
                continue

            self.authorised_next_steps.append(next_step)

        if not self.authorised_next_steps:
            return redirect(self.get_cannot_view_step_url())

    def get_step(self, step_id: str) -> Optional[Step]:
        for step in self.authorised_next_steps:
            if step.id == step_id:
                return step
        return None

    def post(self, request, **kwargs):
        step_id = request.POST.get("step_id", None)
        if not step_id:
            return redirect("flow-continue", pk=self.flow.pk)

        step: Step = self.get_step(step_id=step_id)
        if not step:
            return redirect("flow-continue", pk=self.flow.pk)

        try:
            self.workflow_executor.execute_step(
                user=self.request.user,
                step=step,
                break_flow=False,
                first_run=False,
            )
        except WorkflowNotAuthError as e:
            logger.warning(f"{e}")
            raise PermissionDenied(f"{e}")
        except TaskError as error:
            context = self.get_context_data() | error.context
            return super().render_to_response(context=context)
        return redirect(reverse("flow", args=[self.flow.pk]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            flow=self.flow,
            authorised_next_steps=self.authorised_next_steps,
        )
        return context


class FlowDiagramView(View):
    @staticmethod
    def get(request, pk, **kwargs):
        try:
            flow = Flow.objects.get(pk=pk)
        except Flow.DoesNotExist:
            raise Http404(f"Flow {pk} not found")
        elements = workflow_to_cytoscape_elements(flow)
        return JsonResponse({"elements": elements})


def workflow_to_cytoscape_elements(flow):
    nodes = [step_to_node(flow, step) for step in flow.workflow.steps]

    edges = []
    for step in flow.workflow.steps:
        targets = step.targets
        for target in targets:
            if not target:
                continue

            edges.append(
                {
                    "data": {
                        "id": f"{step.step_id}{target}",
                        "source": step.step_id,
                        "target": target,
                    }
                }
            )

    return [*nodes, *edges]


def step_to_node(flow: Flow, step: Step):
    latest_step_task: TaskRecord = (
        flow.tasks.order_by("started_at").filter(step_id=step.step_id).last()
    )

    targets = step.targets

    end = not bool(targets)
    done = latest_step_task and latest_step_task.done
    current = latest_step_task and not latest_step_task.executed_at

    label = step.description or format_step_id(step.step_id)
    if end and done:
        label += " ✓"

    return {
        "data": {
            "id": step.step_id,
            "label": label,
            "start": step.start,
            "end": end,
            "decision": len(targets) > 1,
            "done": done,
            "current": current,
        }
    }


def format_step_id(step_id):
    # email_all_users -> Email all users
    return step_id.replace("_", " ").title()
