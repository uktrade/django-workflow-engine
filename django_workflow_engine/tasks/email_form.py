from django import forms

from .task import Task


class EmailForm(forms.Form):
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
    from_email = forms.EmailField()
    recipient_list = forms.CharField()


class EmailFormTask(Task, input="email_form"):
    auto = False
    form = EmailForm

    def execute(self, task_info):
        form = self.form(task_info)

        if not form.is_valid():
            raise Exception(form.errors)

        form.cleaned_data["recipient_list"] = form.cleaned_data["recipient_list"].split(
            ","
        )

        return None, form.cleaned_data

    def context(self):
        return {"form": self.form(initial=self.task_record.task_info)}
