from django.urls import path
from .views import TestTemplateView, ContractsListView, ContractDetailView, ContractUpdateView, ContractPendingDetailView, ContainerListView, QueuedContractsListView, GradeAListView, ReallocateView, ClearPendingView, HomePageView
from . import views
urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('contracts/', ContractsListView.as_view(), name='contracts'),
    path('queue/', QueuedContractsListView.as_view(), name='queue_list'),
    path("contract/<int:pk>/", ContractDetailView.as_view(), name="contract_detail"),
    path(
        "contract/<int:pk>/queue/<container>",
        ContractUpdateView.as_view(),
        name="queue",
    ),
    path(
        "contract/<int:pk>/reallocate/",
        ReallocateView.as_view(),
        name="reallocate",
    ),
    path("containers/", ContainerListView.as_view(), name="containers"),
    path("contract/<int:pk>/pending", ContractPendingDetailView.as_view(), name="pending"),
    path('pdf_view/<int:pk>', views.ViewPDF.as_view(), name="pdf_view"),
    path('pdf_download/<int:pk>', views.DownloadPDF.as_view(), name="pdf_download"),
    path('top/', GradeAListView.as_view(), name="grade_a" ),
    path('contract/<int:pk>/pending/clear', ClearPendingView.as_view(), name='clear_pending'),
]