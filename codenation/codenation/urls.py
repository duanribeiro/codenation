"""codenation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from clients import views as clients_views
from loans import views as loans_views

from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib import admin
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title='Loans API',
        default_version='v1',
        description='API to create and pay loans',
    ),
    public=False,
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('loans/', loans_views.LoanAPI.as_view()),
    path('loans/<uuid:loan_id>/', loans_views.LoanDetailAPI.as_view()),
    path('loans/<uuid:loan_id>/payments/', loans_views.LoanPaymentApi.as_view()),
    path('loans/<uuid:loan_id>/balance/', loans_views.LoanPaymentBalanceApi.as_view()),
    path('clients/', clients_views.ClientApi.as_view()),
    path('admin/', admin.site.urls),
]
