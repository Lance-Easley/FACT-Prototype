from django.shortcuts import get_list_or_404, redirect
from django.views.generic import TemplateView, UpdateView, DetailView, ListView
from containers.models import Container
from contracts.models import Contract
from contracts.forms import QueuedContainerForm

# Create your views here.
class TestTemplateView(TemplateView):
    template_name = 'home.html'

class ContainerListView(ListView):
    model = Container
    template_name = 'home.html'

class ContractsListView(ListView):
    model = Contract
    context_object_name = "contracts"
    template_name = 'home.html'

# class QueueForm(Form):
#     def __init__(self, contract, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         containers = Container.objects.filter(
#             company_code=contract.company_code
#         ) 
#         for container in containers:
#             self.fields[container.code] = forms.IntegerField(required=False)

class ContractUpdateView(UpdateView):
    # create view based off of the form
    template_name = "queueform.html"
    model = Contract
    form_class = QueuedContainerForm

    # getting container assigned to specific contract
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["contract"] = kwargs.pop("instance")
        kwargs["from_container"] = self.request.resolver_match.kwargs["container"]
        return kwargs

    # getting the context data/ fields from specific container
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        company = self.get_object()
        context["from_container"] = get_list_or_404(
            Container,
            unit_descriptor=self.request.resolver_match.kwargs["container"],
            company_code=company.company_code,
        )[0]
        return context

    # makes a new json with inserted information and adding it on (editing and saving)
    def form_valid(self, form):
        new_json = [
            {"container": c, "weight": w}
            for c, w in form.cleaned_data.items()
            if w is not None
        ]
        contract = self.get_object()
        contract.pend_containers = new_json
        contract.save()
        return redirect("pending_detail", contract.id)


class ContractPendingDetailView(DetailView):
    model = Contract
    template_name = 'pending.html'

# class ContractPendingListView(ListView):
#     model = QueuedContract
#     template_name = 'queue.html'

class ContractDetailView(DetailView):
    model = Contract
    template_name = 'summary.html'



    