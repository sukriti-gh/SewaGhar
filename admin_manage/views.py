from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.db import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from datetime import datetime, timedelta
from booking.models import DeletedStaff
from django.contrib.auth.decorators import login_required
from booking.models import VendorRequest
from django.contrib.auth.models import User
from booking.models import Appointment
from booking.models import Staff
from booking.models import VendorRequest
from io import BytesIO
import base64                   
from django.db.models import Count
from django.http import JsonResponse
from booking.models import Feedback  
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

def index(request):
    return render(request, 'admin_manage/index.html')


def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=email, password=password)
        if user is not None:
            if user.is_active and (user.is_staff or user.is_superuser):
                login(request, user)
                return redirect('index')  # ✅ direct path, no name lookup
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

    # Fetch Staff Tier Counts
    staff_tier_counts = Staff.objects.values('tier').annotate(total=Count('tier'))
    # Fetch Staff Service Distribution
    staff_service_distribution = Staff.objects.values('service').annotate(total=Count('service'))
    try:
        vendor_data = Staff.objects.all()
    except Exception as e:
        print("Error", e)

    # Prepare Bar Graph Data for Staff Tiers
    bar_labels = [entry['tier'] for entry in staff_tier_counts]
    bar_values = [entry['total'] for entry in staff_tier_counts]

    # Create data for the pie chart
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

def staffPanel(request):
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime
    #Only show the Appointments 21 days from today
    items = Appointment.objects.filter(day__range=[minDate, maxDate]).order_by('day', 'time')
    print("--- DEBUG STAFF CHECK ---")
    print(f"User is logged in: {request.user.is_authenticated}")
    print(f"User ID: {request.user.id}")
    print(f"Is Staff: {request.user.is_staff}")
    return render(request, 'admindashBoard.html', {
        'items':items,
    })
                                            


def update_vendor_tier(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_tier = request.POST.get('new_tier')
        # Update the vendor tier
        try:
            vendor = Staff.objects.get(pk=user_id)
            vendor.tier = new_tier
            vendor.save()
            return JsonResponse({'message': 'Vendor tier updated successfully'})
        except Staff.DoesNotExist:
            return JsonResponse({'message': 'Vendor not found'}, status=404)
    return JsonResponse({'message': 'Invalid request'}, status=400)

def delete_user(request, id):
    print("Delete user")
    user = Staff.objects.get(id=id)  
    deleted_user = DeletedStaff(
        name=user.name,
        email=user.email,
    )
    deleted_user.save()
    user.delete()

    return redirect('admin_serviceproviders')

def admin_feedback(request):
    feedbacks = Feedback.objects.all() 
    context = {
        'feedbacks':feedbacks,
    }
    return render(request, 'admin_manage/admin_feedback.html', context)

# Lists all disputes
def admin_disputes(request):
    disputed_appointments = Appointment.objects.filter(dispute_created=True)
    return render(request, 'admin_manage/admin_disputes.html', {
        'disputed_appointments': disputed_appointments
    })

# Resolves a specific dispute
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
        return redirect(reverse('admin_disputes') + f'?success_message=Dispute resolved')
    else:
        messages.warning(request, 'Error')
        return redirect(reverse('admin_disputes') + f'?warning_message=error ')


def handle_feedback_action(request, feedback_id):
    # Retrieve the feedback object based on the feedback_id
    feedback = get_object_or_404(Feedback, pk=feedback_id)

    if not feedback.acknowledged:
        if feedback.by.email:
            # Render HTML content using the template
            html_message = render_to_string('admin_manage/feedback_acknowledgement_email.html', {'feedback': feedback})

            # Remove HTML tags to create a plain text version
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
            # Assuming success, you can return a success message or status
            return redirect(reverse('admin_feedback') + f'?success_message=Email+sent+successfully')
        else:
            # If the user doesn't have an email, handle it accordingly
            messages.warning(request, 'Error while sending email')
            return redirect(reverse('admin_feedback') + f'?warning_message=User+has+no+email')

    return redirect(reverse('admin_feedback') + f'?warning_message=Feedback+already+acknowledged')


def admin_users(request):
    all_users = User.objects.all()
    context = {
        'users':all_users,
    }
    return render(request, 'admin_manage/admin_users.html',context)


def admin_serviceproviders(request):
    total_service_providers = Staff.objects.count()  
    pending_requests = VendorRequest.objects.count() 
    vendor_requests = VendorRequest.objects.all()
    all_users = User.objects.all()


    try:
        vendor_data=Staff.objects.all()
    except Exception as e:
        print("Error",e)

    context = {
        'pending_requests': pending_requests,
        'total_service_providers': total_service_providers,
        'vendor_requests':vendor_requests,
        'items':vendor_data,
        'users':all_users,
    }
    return render(request, 'admin_manage/admin_serviceproviders.html',context)


# Admin staff request page
def admin_staffrequest(request):
    total_service_providers = Staff.objects.count()
    pending_requests = VendorRequest.objects.count()
    vendor_requests_list = VendorRequest.objects.all()
    all_users = User.objects.all()

    try:
        vendor_data = Staff.objects.all()
    except Exception as e:
        print("Error", e)
        vendor_data = []

    context = {
        'pending_requests': pending_requests,
        'total_service_providers': total_service_providers,
        'vendor_requests': vendor_requests_list,
        'items': vendor_data,
        'users': all_users,
    }
    return render(request, 'admin_manage/admin_staffrequest.html', context)


# Accept vendor request
def accept_vendor_request(request, vendor_email):
    vendor_request = get_object_or_404(VendorRequest, email=vendor_email)
    
    # Get the associated User object before the try block for better scope
    user_to_promote = vendor_request.user 

    # Check if staff member already exists
    if Staff.objects.filter(email=vendor_email).exists():
        messages.error(request, "A staff member with this email already exists.")
        return redirect('admin_staffrequest')

    try:
        # 1. Create the Staff/Vendor object
        Staff.objects.create(
            name=vendor_request.business_name,
            contact_number=vendor_request.contact_number,
            service=vendor_request.business_category,
            image=vendor_request.image,
            experience=getattr(vendor_request, 'experience', None),
            docs=vendor_request.docs,
            CA_image=vendor_request.CA_image,
            CB_image=vendor_request.CB_image,
            bio=vendor_request.business_description,
            email=vendor_email,
            assigned_user=user_to_promote,
        )

        # 2. ⭐️ CRITICAL FIX: Promote the associated Django User to staff status
        user_to_promote.is_staff = True
        user_to_promote.save()
        
        # 3. Send acceptance email
        subject = 'Your Vendor Request has been accepted'
        html_message = render_to_string('admin_manage/vendor_request_accepted_email.html', {'vendor_request': vendor_request})
        plain_text_message = strip_tags(html_message)
        send_mail(subject, plain_text_message, 'sewaghar93@gmail.com', [vendor_email], html_message=html_message, fail_silently=False)

        # 4. Delete vendor request
        vendor_request.delete()
        messages.success(request, "Vendor request accepted successfully. The user is now a staff member. An email has been sent to the vendor.")
        return redirect('admin_staffrequest')

    except IntegrityError:
        messages.error(request, "An error occurred. Staff member might already exist.")
        return redirect('admin_staffrequest')

# Reject vendor request
def reject_vendor_request(request, vendor_email):
    vendor_request = get_object_or_404(VendorRequest, email=vendor_email)

    # Send rejection email
    subject = 'Your Vendor Request has been rejected'
    html_message = render_to_string('admin_manage/vendor_request_rejected.html', {'vendor_request': vendor_request})
    plain_text_message = strip_tags(html_message)
    send_mail(subject, plain_text_message, 'sewaghar93@gmail.com', [vendor_email], html_message=html_message, fail_silently=False)

    # Delete vendor request
    vendor_request.delete()
    messages.success(request, "Vendor request rejected successfully.")
    return redirect('admin_staffrequest')


# Optional: separate view if you need a direct vendor request list (can merge with admin_staffrequest)
def vendor_requests(request):
    vendor_requests_list = VendorRequest.objects.all()
    return render(request, 'admin_staffrequest.html', {'vendor_requests': vendor_requests_list})