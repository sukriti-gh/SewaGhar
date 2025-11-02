
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import accept_vendor_request, reject_vendor_request, admin_disputes
from admin_manage import views as admin_views

urlpatterns = [
    # Dashboard / Home
    path('', views.dashboard_view, name='index'),
    path('admin_default/', views.dashboard_view, name='admin_default'),

    # Admin Authentication
    path('login-admin/', views.admin_login, name='login-admin'),

    # Users
    path('admin_users/', views.admin_users, name='admin_users'),
    
    # Service Providers
    path('admin_serviceproviders/', views.admin_serviceproviders, name='admin_serviceproviders'),
    
    # Vendor Requests & Actions
    path('admin_staffrequest/', views.admin_staffrequest, name='admin_staffrequest'),
    path('admin-panel/accept_vendor_request/<str:vendor_email>/', views.accept_vendor_request, name='accept_vendor_request'),
    path('admin-panel/reject_vendor_request/<str:vendor_email>/', views.reject_vendor_request, name='reject_vendor_request'),
    path('update_vendor_tier/', views.update_vendor_tier, name='update_vendor_tier'),
    
    path('dashboard-panel/', views.staffPanel, name='dashboard-panel'),

    # Delete Users
    path('delete-user/<int:id>/', views.delete_user, name='delete-user'),

    # Feedback & Disputes
   path('admin_feedback/', views.admin_feedback, name='admin_feedback'),
   path('handle-feedback/<int:feedback_id>/', views.handle_feedback_action, name='handle_feedback_action'),
   path('admin_disputes/', views.admin_disputes, name='admin_disputes'),
   path('resolve_dispute/<int:appointment_id>/', views.resolve_dispute, name='resolve_dispute'),

   path('accept_vendor_request/<str:vendor_email>/', views.accept_vendor_request, name='accept_vendor_request'),
   path('reject_vendor_request/<str:vendor_email>/', views.reject_vendor_request, name='reject_vendor_request'),
]

# Serve media files in debug mode
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)