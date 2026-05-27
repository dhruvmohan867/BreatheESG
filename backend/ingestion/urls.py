from django.urls import path
from .views import SAPUploadView

urlpatterns = [
    path('uploads/sap/', SAPUploadView.as_view(), name='sap-upload'),
]
