from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('surveys/', include('surveys.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    # allauth handles Google OAuth at this path
    path('auth/', include('allauth.urls')),
]
