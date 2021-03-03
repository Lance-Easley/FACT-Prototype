from django.urls import path
from .views import TestTemplateView, ContractsListView, ContractDetailView, ContractUpdateView, ContractPendingDetailView, ContainerListView

urlpatterns = [
    path('', ContractsListView.as_view(), name='test'),
    path("contract/<int:pk>/", ContractDetailView.as_view(), name="contract_detail"),
    path(
        "contract/<int:pk>/queue/<container>",
        ContractUpdateView.as_view(),
        name="queue",
    ),
    path("contract/<int:pk>/", ContractPendingDetailView.as_view(), name="pending_detail"),
    path("containers/", ContainerListView.as_view(), name="containers")
]