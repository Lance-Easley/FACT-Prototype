from django.urls import path
from .views import TestTemplateView, ContractsListView, ContractDetailView, ContractUpdateView

urlpatterns = [
    path('', ContractsListView.as_view(), name='test'),
    path("contract/<int:pk>/", ContractDetailView.as_view(), name="contract_detail"),
    path(
        "contract/<int:pk>/queue/<container>",
        ContractUpdateView.as_view(),
        name="queue",
    ),
]