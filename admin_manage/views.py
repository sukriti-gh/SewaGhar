from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.db import IntegrityError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from datetime import datetime, timedelta
from booking.models import DeletedStaff, VendorRequest, Appointment, Staff, Feedback
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from io import BytesIO
import base64
from django.db.models import Count
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# -------------------------
# Admin Dashboard and Login
# -------------------------

def index(request):
    return render(request, 'admin_manage/index.html')


def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active and (user.is_staff or user.is_superuser):
                login(request, user)
                return redirect('admin_default')
            else:
                messages.error(request, 'This account is not an admin.')
        else:
            messages.error(request, 'Invalid login credentials.')

    return render(request, 'admin_manage/login_adm.html')


def dashboard_view(request):
    total_users = User.objects.exclude(username='admin').count()
    total_service_providers = Staff.objects.count()
    non_service_providers = total_users - total_service_providers
    pending_requests = VendorRequest.objects.count()
    vendor_requests = VendorRequest.objects.all()
    all_users = User.objects.all()
    feedbacks = Feedback.objects.all()

    staff_tier_counts = Staff.objects.values('tier').annotate(total=Count('tier'))
    staff_service_distribution = Staff.objects.values('service').annotate(total=Count('service'))

    try:
        vendor_data = Staff.objects.all()
    except Exception as e:
        print("Error:", e)

    bar_labels = [entry['tier'] for entry in staff_tier_counts]
    bar_values = [entry['total'] for entry in staff_tier_counts]

    pie_labels = ['Service Providers', 'Users']
    pie_values = [total_service_providers, non_service_providers]

    context = {
        'total_users': total_users,
        'pending_requests': pending_requests,
        'total_service_providers': total_service_providers,
        'staff_service_distribution': staff_service_distribution,
        'vendor_requests': vendor_requests,
        'items': vendor_data,
        'users': all_users,
        'feedbacks': feedbacks,
        'staff_tier_counts': staff_tier_counts,
        'bar_labels': bar_labels,
        'bar_values': bar_values,
        'pie_labels': pie_labels,
        'pie_values': pie_values,
    }

    return render(request, 'admin_manage/admindefault.html', context)


# -------------------------
# Staff Panel and Tier Update
# -------------------------

def staffPanel(request):
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    maxDate = (today + timedelta(days=21)).strftime('%Y-%m-%d')

    items = Appointment.objects.filter(day__range=[minDate, maxDate]).order_by('day', 'time')

    return render(request, 'admindashBoard.html', {'items': items})


def update_vendor_tier(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_tier = request.POST.get('new_tier')
        try:
            vendor = Staff.objects.get(pk=user_id)
            vendor.tier = new_tier
            vendor.save()
            return JsonResponse({'message': 'Vendor tier updated successfully'})
        except Staff.DoesNotExist:
            return JsonResponse({'message': 'Vendor not found'}, status=404)
    return JsonResponse({'message': 'Invalid request'}, status=400)


def delete_user(request, id):
    user = Staff.objects.get(id=id)
    deleted_user = DeletedStaff(name=user.name, email=user.email)
    deleted_user.save()
    user.delete()
    return redirect('admin_serviceproviders')


# -------------------------
# Feedback Management
# -------------------------

def admin_feedback(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'admin_manage/admin_feedback.html', {'feedbacks': feedbacks})


def handle_feedback_action(request, feedback_id):
    feedback = get_object_or_404(Feedback, pk=feedback_id)

    if not feedback.acknowledged:
        if feedback.by.email:
            html_message = render_to_string('admin_manage/feedback_acknowledgement_email.html', {'feedback': feedback})
            plain_text_message = strip_tags(html_message)

            send_mail(
                'Your feedback has been read',
                plain_text_message,
                'sewaghar93@gmail.com',
                [feedback.by.email],
                html_message=html_message,
                fail_silently=False,
            )
            feedback.acknowledged = True
            feedback.save()
            return redirect(reverse('admin_feedback') + '?success_message=Email+sent+successfully')
        else:
            messages.warning(request, 'Error while sending email')
            return redirect(reverse('admin_feedback') + '?warning_message=User+has+no+email')

    return redirect(reverse('admin_feedback') + '?warning_message=Feedback+already+acknowledged')


# -------------------------
# Admin User Management
# -------------------------

def admin_users(request):
    all_users = User.objects.all()
    return render(request, 'admin_manage/admin_users.html', {'users': all_users})


def admin_serviceproviders(request):
    total_service_providers = Staff.objects.count()
    pending_requests = VendorRequest.objects.count()
    vendor_requests = VendorRequest.objects.all()
    all_users = User.objects.all()

    try:
        vendor_data = Staff.objects.all()
    except Exception as e:
        print("Error:", e)

    context = {
        'pending_requests': pending_requests,
        'total_service_providers': total_service_providers,
        'vendor_requests': vendor_requests,
        'items': vendor_data,
        'users': all_users,
    }
    return render(request, 'admin_manage/admin_serviceproviders.html', context)


def admin_staffrequest(request):
    total_service_providers = Staff.objects.count()
    pending_requests = VendorRequest.objects.count()
    vendor_requests = VendorRequest.objects.all()
    all_users = User.objects.all()

    try:
        vendor_data = Staff.objects.all()
    except Exception as e:
        print("Error:", e)

    context = {
        'pending_requests': pending_requests,
        'total_service_providers': total_service_providers,
        'vendor_requests': vendor_requests,
        'items': vendor_data,
        'users': all_users,
    }
    return render(request, 'admin_manage/admin_staffrequest.html', context)


# -------------------------
# Vendor Request Management
# -------------------------

def reject_vendor_request(request, vendor_email):
    vendor_requests = VendorRequest.objects.filter(email=vendor_email)

    if vendor_requests.exists():
        vendor_request = vendor_requests.first()

        subject = 'Your Vendor Request has been rejected'
        html_message = render_to_string('admin_manage/vendor_request_rejected.html', {'vendor_request': vendor_request})
        plain_text_message = strip_tags(html_message)
        from_email = 'sewaghar93@gmail.com'
        to_email = [vendor_email]
        send_mail(subject, plain_text_message, from_email, to_email, html_message=html_message, fail_silently=False)

        vendor_request.delete()
        return redirect('admin_staffrequest')
    else:
        raise Http404("VendorRequest not found")


def accept_vendor_request(request, vendor_email):
    vendor_requests = VendorRequest.objects.filter(email=vendor_email)
    if not vendor_requests.exists():
        raise Http404("VendorRequest not found")

    vendor_request = vendor_requests.first()

    if Staff.objects.filter(email=vendor_email).exists():
        messages.error(request, "A staff member with this email already exists.")
        return redirect('admin_staffrequest')

    try:
        Staff.objects.create(
            name=vendor_request.business_name,
            contact_number=vendor_request.contact_number,
            service=vendor_request.business_category,
            image=vendor_request.image,
            experience=vendor_request.experience,
            docs=vendor_request.docs,
            CA_image=vendor_request.CA_image,
            CB_image=vendor_request.CB_image,
            bio=vendor_request.business_description,
            email=vendor_email,
            assigned_user=vendor_request.user,
        )

        subject = 'Your Vendor Request has been accepted'
        html_message = render_to_string('admin_manage/vendor_request_accepted_email.html', {'vendor_request': vendor_request})
        plain_text_message = strip_tags(html_message)
        from_email = 'sewaghar93@gmail.com'
        to_email = [vendor_email]
        send_mail(subject, plain_text_message, from_email, to_email, html_message=html_message, fail_silently=False)

        vendor_request.delete()
        messages.success(request, "Vendor request accepted successfully. An email has been sent to the vendor.")
        return redirect('admin_staffrequest')
    except IntegrityError:
        messages.error(request, "Error occurred while processing request. The staff member might already exist.")
        return redirect('admin_staffrequest')


def vendor_requests(request):
    vendor_request = VendorRequest.objects.get(pk=id)
    return render(request, 'admin_manage/admin_staffrequest.html', {'vendor_request': vendor_request})


# -------------------------
# Dispute Management
# -------------------------

def admin_disputes(request):
    disputed_appointments = Appointment.objects.filter(dispute_created=True)
    return render(request, 'admin_manage/admin_disputes.html', {'disputed_appointments': disputed_appointments})


def resolve_dispute(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if not appointment.dispute_resolved:
        appointment.isFinished = "Yes"
        appointment.dispute_resolved = True
        appointment.save()

        html_message = render_to_string('admin_manage/dispute_email.html', {'appointment': appointment})
        plain_text_message = strip_tags(html_message)

        send_mail(
            'Dispute Resolved',
            plain_text_message,
            'sewaghar93@gmail.com',
            [appointment.email],
            html_message=html_message,
            fail_silently=False,
        )
        return redirect(reverse('admin_disputes') + '?success_message=Dispute resolved')
    else:
        messages.warning(request, 'Error')
        return redirect(reverse('admin_disputes') + '?warning_message=error')

    return redirect(reverse('admin_disputes') + '?warning_message=Resolved already')
