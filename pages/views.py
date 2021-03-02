from django.shortcuts import render
from django.views.generic import TemplateView, UpdateView, DetailView, ListView
from containers.models import Container
from contracts.models import Contract
from queued.models import QueuedContract

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

class QueueForm(Form):
    def __init__(self, contract, *args, **kwargs):
        super().__init__(*args, **kwargs)
        containers = Container.objects.filter(
            company_code=contract.company_code
        ) 
        for container in containers:
            self.fields[container.code] = forms.IntegerField(required=False)

class ContractUpdateView(UpdateView):
    # create view based off of the form
    template_name = "queueform.html"
    model = Contract

    def get_form(self):
        return QueueForm(self.get_object())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['company_containers'] = Container.objects.filter(
            company_code=context['contract'].company_code
        )
        return context
    
class ContractPendingDetailView(DetailView):
    model = Contract
    template_name = 'pending.html'

class ContractPendingListView(ListView):
    model = QueuedContract
    template_name = 'queue.html'
class ContractDetailView(DetailView):
    model = Contract
    template_name = 'summary.html'



    