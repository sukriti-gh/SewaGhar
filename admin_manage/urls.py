
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404

urlpatterns = [
    # path('', views.index, name='index'),
    path('login-admin/', views.admin_login, name='login-admin'),
    path('admin_users',views.admin_users, name='admin_users'),
    #dashboard
    path('admin_default/',views.dashboard_view, name='admin_default'),
    path('admin_staffrequest/',views.admin_staffrequest, name='admin_staffrequest'),
    path('admin_feedback/',views.admin_feedback, name='admin_feedback'),
    path('admin_serviceproviders/',views.admin_serviceproviders, name='admin_serviceproviders'),
    # path('dashboard-admin/', views.dashboard_view, name='admin-dashboard'),
    path('accept_vendor_request/<str:vendor_email>/', views.accept_vendor_request, name='accept_vendor_request'),
    path('reject_vendor_request/<str:vendor_email>/', views.reject_vendor_request, name='reject_vendor_request'),
    #delete user
    path('delete-user/<int:id>/', views.delete_user, name='delete-user'),   
    path('update_vendor_tier/', views.update_vendor_tier, name='update_vendor_tier'),
    path('handle-feedback/<int:feedback_id>/', views.handle_feedback_action, name='handle_feedback_action'),
    path('vendor_requests', views.vendor_requests, name='vendor_requests'),   
    path('admin_disputes/', views.admin_disputes, name='admin_disputes'),   
    path('resolve_dispute/<int:appointment_id>/', views.resolve_dispute, name='resolve_dispute'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)