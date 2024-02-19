"""
URL configuration for Gamestore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from egames.api.views import create_staff, create_gamer

urlpatterns = [
    path("admin/", admin.site.urls),
    path('egames/', include('egames.urls')),
    path('auth/sign-up/', create_staff, name='sign-up'),
    path('auth/sign-up/gamer/', create_gamer, name='sign-up-gamer'),
    path('auth/sign-in/gamer/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/sign-in/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='verify_refresh'),
]
