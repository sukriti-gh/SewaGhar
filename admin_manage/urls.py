from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin login
    path('login-admin/', views.admin_login, name='login-admin'),

    # Admin dashboard and management pages
    path('admin_default/', views.dashboard_view, name='admin_default'),
    path('admin_staffrequest/', views.admin_staffrequest, name='admin_staffrequest'),
    path('admin_feedback/', views.admin_feedback, name='admin_feedback'),
    path('admin_serviceproviders/', views.admin_serviceproviders, name='admin_serviceproviders'),
    path('admin_disputes/', views.admin_disputes, name='admin_disputes'),

    # Admin user management
    path('admin_users/', views.admin_users, name='admin_users'),
    path('delete-user/<int:id>/', views.delete_user, name='delete-user'),

    # Vendor management
    path('vendor_requests/', views.vendor_requests, name='vendor_requests'),
    path('accept_vendor_request/<str:vendor_email>/', views.accept_vendor_request, name='accept_vendor_request'),
    path('reject_vendor_request/<str:vendor_email>/', views.reject_vendor_request, name='reject_vendor_request'),
    path('update_vendor_tier/', views.update_vendor_tier, name='update_vendor_tier'),

    # Feedback & dispute handling
    path('handle-feedback/<int:feedback_id>/', views.handle_feedback_action, name='handle_feedback_action'),
    path('resolve_dispute/<int:appointment_id>/', views.resolve_dispute, name='resolve_dispute'),
]

# Media file serving during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
