from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # Delegate user-related routes to a dedicated urls module instead of the views module
    path("api/users/", include("apps.users.urls")),
    # Document-related API routes
    path("api/documents/", include("apps.documents.api.urls")),
]