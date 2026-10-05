from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def health_check(request):
    """
    Endpoint simples utilizado para verificar se a API Django
    está funcionando corretamente.
    """
    return JsonResponse({
        "status": "ok",
        "message": "GPADS Backend está funcionando!"
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
]