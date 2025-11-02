"""
URL configuration for sewaghar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import include, path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from django.conf.urls import handler404
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Default Django admin
    path('admin/', admin.site.urls),

   # Custom Admin Panel (your dashboard)
    path('admin-panel/', include('admin_manage.urls')),

    path('login-admin/', RedirectView.as_view(url='/admin-panel/login-admin/', permanent=False)),


    # Core app
    path('booking/', include('booking.urls')),

    # Main pages
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    path('contact/', views.contact_view, name='contact'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('faq/', views.faq_view, name='faq'),

    # User authentication
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate_user, name='activate'),
    path('verification/', views.verification, name='verification'),
    path('forgot_password/', views.forgot_password_view, name='forgot_password'),
    path('change-password-page/', views.change_password, name='change_password'),

    # Contact form submission
    path('contact_form/', views.contact_form, name='contact_form'),
    path('contact/', views.contact_form, name='contact_email'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 # 404 fallback
    handler404 = 'sewaghar.views.custom_404_view'
    