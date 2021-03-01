from django.shortcuts import render
from django.views.generic import TemplateView, UpdateView, DetailView, ListView
from containers.models import Container
from contracts.models import Contract
from queued.models import QueuedContract

# Create your views here.
class TestTemplateView(TemplateView):
    template_name = 'home.html'

# class ContainerListView(ListView):
#     model = Container
#     template_name = ''

class ContractsListView(ListView):
    model = Contract
    template_name = 'home.html'

class ContractUpdateView(UpdateView):
    

class ContractPendingDetailView(DetailView):
    model = Contract
    template_name = 'pending.html'

class ContractDetailView(DetailView):
    model = Contract
    template_name = 'summary.html'


    