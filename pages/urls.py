from django.urls import path
from .views import TestTemplateView, ContractsListView, ContractDetailView, ContractUpdateView, ContractPendingDetailView, ContainerListView, QueuedContractsListView, GradeAListView
from . import views
urlpatterns = [
    path('', ContractsListView.as_view(), name='home'),
    path('queue/', QueuedContractsListView.as_view(), name='queue_list'),
    path("contract/<int:pk>/", ContractDetailView.as_view(), name="contract_detail"),
    path(
        "contract/<int:pk>/queue/<container>",
        ContractUpdateView.as_view(),
        name="queue",
    ),
    path("containers/", ContainerListView.as_view(), name="containers"),
    path("contract/<int:pk>/pending", ContractPendingDetailView.as_view(), name="pending"),
    path('pdf_view/<int:pk>', views.ViewPDF.as_view(), name="pdf_view"),
    path('pdf_download/', views.DownloadPDF.as_view(), name="pdf_download"),
    path('top/', GradeAListView.as_view(), name="grade_a" )
]