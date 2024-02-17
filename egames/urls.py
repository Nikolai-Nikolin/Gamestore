from django.urls import path, include
from egames import views

urlpatterns = [
    path("ping", views.ping, name="admin"),
    path('api/', include('egames.api.urls')),
]
