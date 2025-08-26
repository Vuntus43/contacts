from django.urls import path
from contacts_io import views as v

urlpatterns = [
    path("", v.upload_view, name="upload"),
    path("export/", v.export_page, name="export_page"),
    path("export/download/", v.export_download, name="export_download"),
]
