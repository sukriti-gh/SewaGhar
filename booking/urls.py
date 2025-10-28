from django.urls import path
from . import views

urlpatterns = [
    path('booking', views.booking, name='booking'),
    path('login-provider', views.login_view, name='login-provider'),
    path('bookingSubmit', views.bookingSubmit, name='bookingSubmit'),
    path('khalti-payment', views.payment, name='khalti-payment'),
    path('', views.userPanel, name='userPanel'),
    path('history/', views.history, name='history'),
    path('appointment-delete/<int:id>', views.appointmentDelete, name='appointmentDelete'),
    path('appointment-delete-booking/<int:id>', views.appointmentDeleteBooking, name='appointmentDeleteBooking'),
    path('appointment-finished/<int:id>', views.appointmentFinished, name='appointmentFinished'),

    path('user-update-submit/<int:id>', views.userUpdateSubmit, name='userUpdateSubmit'),
    path('rate_staff/<int:appointment_id>/', views.rate_staff, name='rate_staff'),
    path('become-vendor', views.become_vendor, name='become-vendor'),
    path('update_staff<int:id>/', views.update_staff, name='update_staff'),
    path('submit-staff-data/', views.submit_staff_data, name='submit_staff_data'),

    path('dashboard-panel', views.vendor_dashboard, name='dashboard-panel'),
    path('vendor_appointments', views.vendor_appointments, name='vendor_appointments'),
    path('vendor_req', views.vendor_req, name='vendor_req'),

    path('logout-view', views.logout_view, name='logout-view'),
    path('edit_appointment<int:id>/', views.edit_appointment, name='edit_appointment'),
    path('inquiry_submit', views.inquiry_submit, name='inquiry_submit'),
    path('inquiry/', views.inquiry_view, name='inquiry'),
    path('change/', views.change_view, name='change'),

    path('accept_booking/', views.accept_booking, name='accept_booking'),
    path('refund_booking', views.refund_booking, name='refund_booking'),
    path('reject_booking/', views.reject_booking, name='reject_booking'),

    path('vendor_profile<int:id>/', views.vendor_profile, name='vendor_profile'),
    path('user_profile', views.user_profile, name='user_profile'),

    path('user_changes_password', views.user_changes_password, name='user_changes_password'),
    path('vendor_changes_password/<int:id>/', views.vendor_changes_password, name='vendor_changes_password'),
    path('vendor_changepassword/<int:id>/', views.vendor_changepassword, name='vendor_changepassword'),

    path('submit_invoice<int:id>/', views.submit_invoice, name='submit_invoice'),
    path('free_booking/', views.free_booking, name='free_booking'),
    path('logout/', views.logout_view, name='logout'),
]
