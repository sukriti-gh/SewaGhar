from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import get_object_or_404
from .models import *
from .forms import *
import json
import uuid
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
import requests
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login


def logout_view(request):
    logout(request)

    return JsonResponse({'message': 'Logout successful'})



def login_view(request):
    if request.method == 'GET':
        return render(request, 'loginServiceProvider.html')
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if a user with the provided email exists in the User model
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User with the provided email does not exist. Please try again.")
            return redirect('login-provider')  # Redirect back to the login page if the user does not exist

        # Authenticate the user using the email and password
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            # Check if the user's email exists in the Staff model
            try:
                staff_member = Staff.objects.get(email=email)
                # If the user is a staff member, proceed with login
                login(request, user)
                messages.success(request, "You have been logged in successfully as staff!")
                return redirect('dashboard-panel')  # Redirect to the dashboard panel after successful login
            except Staff.DoesNotExist:
                # The user exists but is not listed as a staff member in the Staff model
                messages.error(request, "You do not have staff access. Please contact the administrator.")
                return redirect('login-provider')  # Redirect back to the login page if the user is not a staff member
        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return redirect('login-provider')  # Redirect back to the login page if the authentication fails
    else:
        return HttpResponse("Method Not Allowed", status=405)  # Return an HTTP 405 Method Not Allowed for unsupported methods

@login_required(login_url=reverse_lazy('login'))
def vendor_dashboard(request):
    try:
        # Make the name field case-insensitive
        staff_member = Staff.objects.get(name__iexact=request.user.username)
    except Staff.DoesNotExist:
        return HttpResponseBadRequest("You are not registered as a staff member.")

    try:
        # Fetch appointments associated with the logged-in staff member
        appointments = Appointment.objects.filter(staff=staff_member.name)
        total_appointments = appointments.count()
        # Count pending and completed appointments
        pending_appointments = appointments.filter(isFinished="No").count()
        completed_appointments = appointments.filter(isFinished="Yes").count()

        # Count appointments based on 'day' field
        date_counts = appointments.values('day').annotate(appointment_count=models.Count('id'))
        date_appointments = [(date_count['day'], date_count['appointment_count']) for date_count in date_counts]
        print('Date Appointments:', date_appointments)

    except Appointment.DoesNotExist:
        appointments = []
        total_appointments = 0
        pending_appointments = 0
        completed_appointments = 0
        date_appointments = []

    context = {
        'appointments': appointments,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'staff_member': staff_member,
        'date_appointments': date_appointments,
    }
    return render(request, 'vendordashBoard.html', context)

@login_required(login_url=reverse_lazy('login'))
def vendor_appointments(request):
    total_appointments = Appointment.objects.count()
    
    # Fetch the staff member associated with the logged-in user
    try:
        # Make the name field case-insensitive
        staff_member = Staff.objects.get(name__iexact=request.user.username)
        print(request.user.username)
    except Staff.DoesNotExist:
        # Handle case where logged-in user is not a staff member
        return HttpResponseBadRequest("You are not registered as a staff member.")

    try:
        # Fetch appointments associated with the logged-in staff member
        appointments = Appointment.objects.filter(staff=staff_member.name)
        print(staff_member)
    except Appointment.DoesNotExist:
        # Handle the case where no appointments are found for the staff member
        appointments = []

    context = {
        'appointments': appointments,
        'total_appointments': total_appointments,
        'staff_member': staff_member,
    }
    return render(request, 'vendor_appointments.html', context)

@login_required(login_url=reverse_lazy('login'))
def vendor_req(request):
    total_appointments = Appointment.objects.count()
    
    # Fetch the staff member associated with the logged-in user
    try:
        # Make the name field case-insensitive
        staff_member = Staff.objects.get(name__iexact=request.user.username)
        print(request.user.username)
    except Staff.DoesNotExist:
        # Handle case where logged-in user is not a staff member
        return HttpResponseBadRequest("You are not registered as a staff member.")

    try:
        # Fetch appointments associated with the logged-in staff member
        appointments = Appointment.objects.filter(staff=staff_member.name)
        print(staff_member)
    except Appointment.DoesNotExist:
        # Handle the case where no appointments are found for the staff member
        appointments = []

    context = {
        'appointments': appointments,
        'total_appointments': total_appointments,
        'staff_member': staff_member,
    }
    return render(request, 'vendor_request.html', context)


def generate_invoice_number():
    # Generate a random number
    random_number = str(uuid.uuid4().fields[-1])[:6]  
    return f'HB/{random_number}/SE/10'



@login_required(login_url=reverse_lazy('login'))
def submit_staff_data(request):
    if request.method == 'POST':
        staff_name = request.POST.get('staff_name')
        print(staff_name)
        day = request.session.get('day')
        service = request.session.get('service')
        tier = request.session.get('tier')
        print(tier)
        address = request.session.get('address')
        time = request.session.get('time')
        number = request.session.get('number')
        email = request.session.get('email')
        latitude = request.session.get('latitude')
        longitude = request.session.get('longitude')
        description=request.session.get('description')
        print(number)
        try:
            staff_member = Staff.objects.get(name=staff_name, service=service)
            invoice_number = generate_invoice_number()
            appointment = Appointment.objects.create(
                user=request.user,
                service=staff_member.service,
                staff=staff_member.name,
                address=address,
                number=number,
                description=description,
                latitude=latitude,
                longitude=longitude,
                email=email,
                time=time,
                day=day,
                tier=staff_member.tier,
                invoice_number=invoice_number,
            )

            # Send email to user
            user_subject = 'Appointment Confirmation'
            user_message = render_to_string('user_appointment_created.html', {'appointment': appointment})
            user_email = request.user.email
            send_mail(user_subject, strip_tags(user_message), 'sewaghar93@gmail.com', [user_email], html_message=user_message)

            # Send email to staff
            staff_subject = 'New Appointment'
            staff_message = render_to_string('staff_appointment_created.html', {'appointment': appointment})
            staff_email = staff_member.email
            send_mail(staff_subject, strip_tags(staff_message), 'sewaghar93@gmail.com', [staff_email], html_message=staff_message)

            messages.success(request, "Appointment created")
            return redirect('userPanel')
        except Staff.DoesNotExist:
            return HttpResponse("Staff with the given name does not exist.")


@login_required(login_url=reverse_lazy('login'))
def vendor_requests_view(request):
    vendor_requests = VendorRequest.objects.all()
    return render(request, 'admindashBoard.html', {'items': vendor_requests})

@login_required(login_url=reverse_lazy('login'))
def become_vendor(request):
    if request.method == 'POST':
        
        business_name = request.POST.get("username")
        business_address = request.POST.get('business_address')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        CA_image = request.FILES.get('CA_image')
        CB_image = request.FILES.get('CB_image')
        business_description = request.POST.get('business_description')
        business_category = request.POST.get('business_category')
        experience = request.POST.get('experience')
        docs = request.FILES.get('docs')
        if request.user.email != email:
            messages.error(request, "Invalid email. Please use the email associated with your account.")
            return redirect('booking')  # Redirect to the same page to fix the form

        # Check if the user already submitted a vendor request
        if VendorRequest.objects.filter(user=request.user).exists():
            messages.error(request, "You have already submitted a vendor request.")
        else:
            # Check if the user already exists in the staff table
            if Staff.objects.filter(email=email).exists():
                messages.error(request, "You already have Staff access.")
            elif DeletedStaff.objects.filter(email=email).exists():
                messages.error(request, "You are restricted from becoming a service provider.")
            else:
                # Create and save the VendorRequest instance
                vendor_request = VendorRequest(
                    user=request.user,
                    business_name=business_name,
                    business_address=business_address,
                    contact_number=contact_number,
                    email=email,
                    image=image,
                    CA_image=CA_image,
                    experience=experience,
                    docs=docs,
                    CB_image=CB_image,
                    business_description=business_description,
                    business_category=business_category,
                )
                vendor_request.save()
                messages.success(request, 'Vendor request submitted successfully.')
                subject = 'Vendor Request Submission'
                message = render_to_string('vendor_request_email.html', {'vendor_request': vendor_request})
                from_email = 'your_email@example.com'
                to_email = [email]
                send_mail(subject, strip_tags(message), from_email, to_email, html_message=message)

        return redirect('booking')  

    return render(request, 'become_vendor.html')

@login_required(login_url=reverse_lazy('login'))
def index(request):
    return render(request, "vendordashBoard.html",{})


@login_required(login_url=reverse_lazy('login'))
def logout_view(request):
    logout(request)
    # Redirect to a success page or some other page
    return redirect('login') 

@login_required(login_url=reverse_lazy('login'))
def booking(request):
    times = [
    "7 am", "8 am", "9 am", "10 am", "11 am", "12 pm", 
    "1 pm", "2 pm", "3 pm", "4 pm", "5 pm", "6 pm", "7 pm", "8 pm"]

    staff_members = Staff.objects.all() 

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')
        time = request.POST.get('time')
        number = request.POST.get('number')
        email = request.POST.get('email')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        description=request.POST.get('description')
        # Check if the user already has an appointment for the selected service
        existing_appointment = Appointment.objects.filter(
            user=request.user,
            service=service,
            isFinished='No'
        ).exists()

        if existing_appointment:
            messages.error(request, f"You already have an appointment for the {service} service.")
            return redirect('booking')
        # Save the booking details to the session
        request.session['day'] = day
        request.session['service'] = service
        request.session['time'] = time
        request.session['address'] = address
        request.session['number'] = number
        request.session['email'] = email
        request.session['latitude'] = latitude
        request.session['longitude'] = longitude
        request.session['description'] = description
        return redirect('bookingSubmit')

    return render(request, 'booking.html', {
        'times': times,
        'staff_members': staff_members,
    })

from django.db.models import Subquery, OuterRef


@login_required(login_url=reverse_lazy('login'))
def bookingSubmit(request):
    user = request.user
    times = ["7 am", "8 am", "9 am", "10 am", "11 am", "12 pm", "1 pm", "2 pm", "3 pm", "4 pm", "5 pm", "6 pm", "7 pm", "8 pm"]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime
    print(maxDate)
    day = request.session.get('day')
    service = request.session.get('service')
    address = request.session.get('address')
    time = request.session.get('time')
    email = request.session.get('email')
    number = request.session.get('number')
    latitude = request.session.get('latitude')
    longitude = request.session.get('longitude')
    description=request.session.get('description')
    print(user)
    user_profile = user.profile if user.is_authenticated else None
    # Filter staff members based on the selected service
    if service == 'Plumber':
        staff_members = Staff.objects.filter(service='Plumber')
    elif service == 'Electrician':
        staff_members = Staff.objects.filter(service='Electrician')
    else:
        staff_members = Staff.objects.all()

    # Exclude the current user's name from the list of staff members
    if user.is_authenticated:
        staff_members = staff_members.exclude(email=user.email)
    
    print("Before exclusion:", staff_members)
    busy_staff_ids = Appointment.objects.filter(
        day=day,
        time=time,
        isFinished='No',
    ).values_list('staff', flat=True)
    
    print("Busy staff IDs:", busy_staff_ids)
    staff_members = staff_members.exclude(name__in=Subquery(busy_staff_ids))
    print("After exclusion:", staff_members)
    if request.method == 'POST':
        for instance_tier in staff_members:
            staff_tier = instance_tier.tier
        staff_name = request.POST.get('staff_name')
        print(staff_tier)
        # Create the appointment
        if service is not None:
            if day <= maxDate and day >= minDate:
                invoice_number = generate_invoice_number()
                appointment = Appointment.objects.create(
                    day=day,
                    time=time,
                    user=user,
                    number=number,
                    email=email,
                    address=address,
                    description=description,
                    service=service,
                    latitude=latitude,
                    longitude=longitude,
                    staff=staff_name,
                    tier=staff_tier,
                    payment_status='Cash on Delivery',
                    invoice_number=invoice_number,
                )
            else:
                messages.error(request, "The Selected Date Isn't In The Correct Time Period!")
                return redirect('userPanel')
            user_subject = 'Appointment Confirmation'
            user_message = render_to_string('user_appointment_created.html', {'appointment': appointment})
            user_email = request.user.email
            send_mail(user_subject, strip_tags(user_message), 'sewaghar93@gmail.com', [user_email], html_message=user_message)

            # Send email to staff
            staff_subject = 'New Appointment'
            staff_message = render_to_string('staff_appointment_created.html', {'appointment': appointment})

            # Iterate through the queryset to get individual Staff instances
            for staff_instance in staff_members:
                staff_email = staff_instance.email
                send_mail(staff_subject, strip_tags(staff_message), 'sewaghar93@gmail.com', [staff_email], html_message=staff_message)

            messages.success(request, "Appointment created")
            return redirect('userPanel')

    return render(request, 'bookingSubmit.html', {
        'times': times, 'staff': staff_members,'user_profile': user_profile
    })



@login_required(login_url=reverse_lazy('login'))
def userPanel(request):
    user = request.user
    appointments = Appointment.objects.filter(user=user).order_by('day', 'time')
    
    # Calculate the current time
    current_time = timezone.now()

    for appointment in appointments:
        # Calculate the appointment time by combining the appointment day and time
        appointment_datetime = timezone.make_aware(datetime.combine(appointment.day, datetime.strptime(appointment.time, '%I %p').time()))

        # Check if the appointment time has already passed
        appointment.appointment_time_passed = current_time > appointment_datetime

    return render(request, 'userPanel.html', {
        'user': user,
        'appointments': appointments,
    })


@login_required(login_url=reverse_lazy('login'))
def history(request):
    user = request.user
    appointments = Appointment.objects.filter(user=user).order_by('day', 'time')
    return render(request, 'history.html', {
        'user':user,
        'appointments':appointments,
    })


@login_required(login_url=reverse_lazy('login'))
def rate_staff(request, appointment_id):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, id=appointment_id)
        rating = int(request.POST.get('rating', 0))

        if 1 <= rating <= 5:  # Assuming a rating scale from 1 to 5
            appointment.rating = rating
            appointment.rated = True  # Set the 'rated' field to True
            appointment.save()

            # Attempt to match staff based on a case-insensitive comparison
            staff = Staff.objects.filter(Q(name__iexact=appointment.staff) | Q(assigned_user__iexact=appointment.staff)).first()

            if staff:
                staff.update_rating(rating)
                messages.success(request, 'Rating submitted successfully.')
            else:
                messages.error(request, 'Staff not found.')
        else:
            messages.error(request, 'Invalid rating.')

    else:
        messages.error(request, 'Invalid request.')

    return redirect('history')  


@login_required(login_url=reverse_lazy('login'))
def appointmentDelete(request,id):
    appointment = Appointment.objects.get(pk=id)
    appointment.delete()
    messages.success(request, "Appointment Deleted!")
    return redirect('dashboard-panel')


@login_required(login_url=reverse_lazy('login'))
def appointmentDeleteBooking(request, id):
    staff_name=request.POST.get('staff_name')
    # Get the appointment to be deleted
    appointment = Appointment.objects.get(pk=id)
    # Save the appointment data to the DeletedAppointment model
    deleted_appointment = DeletedAppointment(
        user=appointment.user,
        service=appointment.service,
        day=appointment.day,
        address=appointment.address,
        description=appointment.description,
        latitude=appointment.latitude,
        longitude=appointment.longitude,
        number=appointment.number,
        email=appointment.email,
        isFinished=appointment.isFinished,
        accepted=appointment.accepted,
        rejected=appointment.rejected,
        time=appointment.time,
        staff=appointment.staff,
        payment_status=appointment.payment_status,
        rating=appointment.rating,
        rated=appointment.rated,
    )
    deleted_appointment.save()
    appointment.delete()
    user_subject = 'Deleted Appointment'
    user_message = render_to_string('user_appointment_deleted.html', {'appointment': appointment})
    user_email = request.user.email
    send_mail(user_subject, strip_tags(user_message), 'your_email@example.com', [user_email], html_message=user_message)
    staff_subject = 'Deleted Appointment'
    staff_message = render_to_string('staff_appointment_deleted.html', {'appointment': appointment})    
    staff_member = Staff.objects.get(name=staff_name)
    staff_email = staff_member.email
    send_mail(staff_subject, strip_tags(staff_message), 'your_email@example.com', [staff_email], html_message=staff_message)                   
    messages.success(request, "Appointment Deleted!")
    return redirect('booking')


@login_required(login_url=reverse_lazy('login'))
def appointmentFinished(request,id):
    #make it take the appointment throgu id and make a field true
    appointment = Appointment.objects.get(pk=id)
    appointment.isFinished = "Yes"
    appointment.save()
    user_email = appointment.email if appointment else ''
    subject = 'Booking Completed'
        
        # Render HTML content using the template
    html_message = render_to_string('booking_completed_email.html', {'appointment': appointment})
        
    plain_text_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]        
    send_mail(subject, plain_text_message, from_email, recipient_list, html_message=html_message, fail_silently=False)
    messages.success(request, "Appointment Finished!")
    return redirect('vendor_appointments')

@login_required(login_url=reverse_lazy('login'))
def update_staff(request, id):
    staff = get_object_or_404(Staff, id=id)

    if request.method == 'POST':
        staff.contact_number = request.POST.get('number')
        staff.bio = request.POST.get('bio')
        new_image = request.FILES.get('image')
        if new_image:
            staff.image = new_image

        staff.save()

        messages.success(request, 'Service Provider Profile updated successfully.')
        return redirect('dashboard-panel')
    else:
        # If it's not a POST request, retrieve staff information
        context = {
            'staff': staff,
            'id': id,
        }

        return render(request, 'vendor_profile.html', context)

@login_required(login_url=reverse_lazy('login'))
def userUpdateSubmit(request, id):
    user = request.user
    times = [
        "7 am", "8 am", "9 am", "10 am", "11 am", "12 pm", 
        "1 pm", "2 pm", "3 pm", "4 pm", "5 pm", "6 pm", "7 pm", "8 pm"
    ]

    # Get current date
    today = datetime.now()
    # Retrieve 'day' and 'service' from session
    day = request.POST.get('day')  # Retrieve 'day' from the form data
    service = request.POST.get('service')
    address = request.POST.get('address')
    latitude = request.POST.get('latitude')
    staff_name = request.POST.get('staff')
    staff=request.POST.get('staff')
    longitude = request.POST.get('longitude')
    number = request.POST.get('number')

    if request.method == 'POST':
        time = request.POST.get("time")
        if service:
            # Check if the 'day' variable is properly set before processing
            if day:
                if Appointment.objects.filter(day=day, time=time, staff=staff_name).exclude(pk=id).count() == 0:
                    Appointment.objects.filter(pk=id).update(
                        user=user,
                        service=service,
                        address=address,
                        longitude=longitude,
                        latitude=latitude,
                        number=number,
                        day=day,
                        time=time,
                    )
                    
                    # Fetch the updated appointment details after the update
                    appointment = Appointment.objects.get(pk=id)

                    user_subject = 'Updated Appointment'
                    user_message = render_to_string('user_appointment_edited.html', {'appointment': appointment})
                    user_email = request.user.email
                    send_mail(user_subject, strip_tags(user_message), 'your_email@example.com', [user_email], html_message=user_message)

                    staff_subject = 'Updated Appointment'
                    staff_message = render_to_string('staff_appointment_edited.html', {'appointment': appointment})
                    
                    # Filter Staff model based on staff name
                    staff_member = Staff.objects.get(name=staff_name)
                    
                    staff_email = staff_member.email
                    send_mail(staff_subject, strip_tags(staff_message), 'your_email@example.com', [staff_email], html_message=staff_message)                   
                    return JsonResponse({'status': 'success', 'message': 'Appointment successfully updated.'})
                else:
                    messages.error(request, "This time slot is already booked. Please choose a different time.")
            else:
                messages.error(request, "Please select a date.")
        else:
            messages.error(request, "Please select a service.")
        return JsonResponse({'status': 'error', 'message': 'This time slot is already booked. Please choose a different time'})

    return render(request, 'userUpdateSubmit.html', {
        'times': times,
        'id': id,
    })


@login_required(login_url=reverse_lazy('login'))
def edit_appointment(request, id):
    appointment = Appointment.objects.get(pk=id)
    
    # Calculate the current time
    current_time = timezone.now()

    # Calculate the appointment time by combining the appointment day and time
    appointment_datetime = timezone.make_aware(datetime.combine(appointment.day, datetime.strptime(appointment.time, '%I %p').time()))

    # Check if the current time is less than 2 hours before the appointment
    if appointment_datetime - current_time < timedelta(hours=2):
        messages.error(request, "You cannot edit this appointment")
        return redirect('userPanel')  # Replace 'your_redirect_view_name' with the appropriate view name or URL

    times = [
        "7 am", "8 am", "9 am", "10 am", "11 am", "12 pm", 
        "1 pm", "2 pm", "3 pm", "4 pm", "5 pm", "6 pm", "7 pm", "8 pm"
    ]

    context = {
        'appointment': appointment,
        'times': times,
    }
    return render(request, 'userUpdateSubmit.html', context)

from datetime import datetime

@login_required(login_url=reverse_lazy('login'))
def payment(request):
    user = request.user
    email = request.POST.get('email')
    today = datetime.now().date()
    min_date = today.strftime('%Y-%m-%d')
    delta_time = today + timedelta(days=21)
    max_date = delta_time.strftime('%Y-%m-%d')
    day = request.session.get('day')
    number = request.session.get('number')
    service = request.session.get('service')
    address = request.session.get('address')
    time = request.session.get('time')
    email = request.session.get('email')
    latitude = request.session.get('latitude')
    longitude = request.session.get('longitude')
    description = request.session.get('description')

    if service == 'Plumber':
        staff_members = Staff.objects.filter(service='Plumber')
    elif service == 'Electrician':
        staff_members = Staff.objects.filter(service='Electrician')
    else:
        staff_members = Staff.objects.all()

    if request.method == 'POST':
        data = json.loads(request.body)
        payment_token = data.get('payment_token')
        payment_amount = data.get('payment_amount')
        staff_id = data.get('staff_id')

        khalti_secret_key = "test_secret_key_ce1adf77ac904ffbba3bc3687d287103"
        verification_url = "https://khalti.com/api/v2/payment/verify/"

        headers = {
            'Authorization': f'key {khalti_secret_key}',
        }
        payload = {
            'token': payment_token,
            'amount': payment_amount,
        }
        response = requests.post(verification_url, headers=headers, json=payload)

        if response.status_code == 200:
            if service is not None and day <= max_date and day >= min_date:
                try:
                    staff_member = Staff.objects.get(id=staff_id)

                    # Creating appointment for the selected staff member only
                    appointment = Appointment.objects.create(
                        day=day,
                        time=time,
                        user=user,
                        address=address,
                        description=description,
                        number=number,
                        latitude=latitude,
                        longitude=longitude,
                        email=email,
                        service=service,
                        staff=staff_member.name,
                        tier=staff_member.tier,
                        payment_status='Paid',
                    )

                    # Dynamic invoice number
                    invoice_number = f"HB{datetime.now().strftime('%Y%m%d%H%M%S')}/SE/10"

                    # Save the invoice number in the appointment
                    appointment.invoice_number = invoice_number
                    appointment.save()

                    # CBMS API integration
                    cbms_api_url = "https://cbapi.ird.gov.np/api/bill"
                    cbms_headers = {'Content-Type': 'application/json'}

                    cbms_data = {
                        "username": "Test_CBMS",
                        "password": "test@321",
                        "seller_pan": "999999999",
                        "buyer_pan": "HRIDAYA BHATTARAI 1",
                        "buyer_name": "123456789",
                        "fiscal_year": "2080.081",
                        "invoice_number": invoice_number,
                        "invoice_date": "2080.09.05",
                        "total_sales": float(payment_amount),
                        "taxable_sales_vat": float(payment_amount),
                        "vat": 0,
                        "excisable_amount": 0,
                        "excise": 0,
                        "taxable_sales_hst": 0,
                        "hst": 0,
                        "amount_for_esf": 0,
                        "esf": 0,
                        "export_sales": 0,
                        "tax_exempted_sales": 0,
                        "isrealtime": True,
                        "datetimeclient": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    }
                    print(cbms_data)
                    try:
                        cbms_response = requests.post(
                            cbms_api_url, json=cbms_data, headers=cbms_headers)
                        cbms_response.raise_for_status()

                        cbms_response_data = cbms_response.json()
                        if cbms_response_data:
                            print(
                                f"CBMS API: Bill posted successfully! Invoice Number: {invoice_number}")
                            # Send invoice number to the user
                            user_subject = 'New Appointment'
                            user_message = render_to_string('user_appointment_created.html',
                                                             {'appointment': appointment})
                            user_email = request.user.email
                            send_mail(user_subject, strip_tags(user_message), 'your_email@example.com',
                                      [user_email], html_message=user_message)

                            staff_subject = 'New Appointment'
                            staff_message = render_to_string('staff_appointment_created.html',
                                                              {'appointment': appointment})
                            staff_email = staff_member.email
                            send_mail(staff_subject, strip_tags(staff_message), 'your_email@example.com',
                                      [staff_email], html_message=staff_message)

                            messages.success(request, "Appointment created successfully!")
                        else:
                            print(f"CBMS API: Error code {cbms_response_data}")
                            messages.error(request, "Error in CBMS API integration")

                    except requests.exceptions.RequestException as e:
                        print(f"CBMS API: Error posting bill - {e}")
                        messages.error(request, "Error in CBMS API integration")

                except Staff.DoesNotExist:
                    messages.error(request, "Selected staff member does not exist")

                return JsonResponse({'message': 'Appointment booked successfully'})
            else:
                messages.error(request, "The selected date isn't in the correct time period!")
        else:
            messages.error(request, "There was an error in payment verification")

    return render(request, 'userPanel.html', {'times': times})


@login_required(login_url=reverse_lazy('login'))
def inquiry_submit(request):
    user = request.user

    if request.method == 'POST':
        feedback = MyFeedbackForm(request.POST)
        if feedback.is_valid():
            # Get the form data including 'type'
            message = feedback.cleaned_data['message']
            type = feedback.cleaned_data['type']

            # Create and save the Feedback object with 'type' field
            new_feedback = Feedback.objects.create(by=user, message=message, type=type)
            
            # Redirect or do something upon successful save
            return redirect('inquiry')  # Redirect to a success page
        else:
            print(feedback.errors)
    else:
        feedback = MyFeedbackForm()
    
    return render(request, 'inquiry.html', {'feedback': feedback})

@login_required(login_url=reverse_lazy('login'))
def inquiry_view(request):
    return render(request, 'inquiry.html')

@login_required(login_url=reverse_lazy('login'))
def change_view(request):
    return render(request, 'change.html')

@login_required(login_url=reverse_lazy('login'))
def user_changes_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        print(username)
        user = authenticate(request, username=username, password=old_password)
        if user is not None:
            # User and old password match, update the password
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()

                # Log the user in with the new password
                login(request, user)

                messages.success(request, 'Password changed successfully.')
                return redirect('login')  # Replace 'success_page' with the actual success page URL

            else:
                messages.error(request, 'New passwords do not match.')
        else:
            messages.error(request, 'Invalid old password.')

    return render(request, 'change.html')


@login_required(login_url=reverse_lazy('login'))
def accept_booking(request):
    if request.method == 'POST':
        # Get the appointment ID from the form data
        appointment_id = request.POST.get('appointment_id', '')
        
        # Retrieve the Appointment instance based on the ID
        appointment = Appointment.objects.get(pk=appointment_id)
        appointment.accepted=True
        appointment.save()
        user_email = appointment.email if appointment else ''
        subject = 'Booking Accepted'
        html_message = render_to_string('booking_accepted_email.html', {'appointment': appointment})
        plain_text_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_email]
        send_mail(subject, plain_text_message, from_email, recipient_list, html_message=html_message, fail_silently=False)
        messages.success(request,"Booking Accepted")

        # Redirect to a success page or do any other necessary actions
        return redirect('vendor_req')

    # Handle cases where the form is not submitted via POST
    return render(request, 'vendor_request.html')  


@login_required(login_url=reverse_lazy('login'))
def reject_booking(request):
    if request.method == 'POST':
        # Get the appointment ID from the form data
        appointment_id = request.POST.get('appointment_id', '')
        
        # Retrieve the Appointment instance based on the ID
        appointment = Appointment.objects.get(pk=appointment_id)
        
        user_email = appointment.email if appointment else ''

        subject = 'Booking Rejected'
        
        # Render HTML content using the template
        html_message = render_to_string('booking_rejected_email.html', {'appointment': appointment})
        
        # Remove HTML tags to create a plain text version
        plain_text_message = strip_tags(html_message)
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_email]
        
        # Send the email with both HTML and plain text versions
        send_mail(subject, plain_text_message, from_email, recipient_list, html_message=html_message, fail_silently=False)
        
        appointment.rejected = True
        appointment.delete()
        messages.success(request,"Booking Rejected")

        return redirect('vendor_req')
    
    return render(request, 'vendor_request.html')  

@login_required(login_url=reverse_lazy('login'))
def refund_booking(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        payment_token = data.get('payment_token')
        payment_amount = data.get('payment_amount')
        appointment_id = data.get('appointment_id') 

        khalti_secret_key = "test_secret_key_ce1adf77ac904ffbba3bc3687d287103"
        verification_url = "https://khalti.com/api/v2/payment/verify/"
        headers = {
            'Authorization': f'key {khalti_secret_key}',
        }
        payload = {
            'token': payment_token,
            'amount': payment_amount,
        }
        print(appointment_id, payment_token, payment_amount)
        response = requests.post(verification_url, headers=headers, json=payload)

        # Assuming you have a model field named 'email' in your Appointment model
        appointment = Appointment.objects.get(pk=appointment_id)
        user_email = appointment.email if appointment else ''
        subject = 'Booking Rejected'
        # Render HTML content using the template
        html_message = render_to_string('booking_rejected_email.html', {'appointment': appointment})
        # Remove HTML tags to create a plain text version
        plain_text_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_email]
        
        # Send the email with both HTML and plain text versions
        send_mail(subject, plain_text_message, from_email, recipient_list, html_message=html_message, fail_silently=False)
        
        appointment.rejected = True
        appointment.delete()
        messages.success(request,"Booking Rejected")
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request method'}, status=400)




@login_required(login_url=reverse_lazy('login'))
def vendor_profile(request,id):
    staff = Staff.objects.get(pk=id)
    print(staff)
    context = {
    'staff': staff,
    'id' :id,
    }
    return render(request, 'vendor_profile.html', context)


def user_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update contact number
        contact_number = request.POST.get('contact')
        user_profile.contact_number = contact_number
        # Check if a new image is provided
        image = request.FILES.get('image')

        if image:
            # If a new image is selected, update the user profile's image field
            user_profile.image = image

        user_profile.save()
        messages.success(request, "Profile updated successfully")
        return redirect('user_profile')  # Redirect to the same page after updating the profile

    # If the request method is not POST (i.e., it's a GET request), render the template with the existing user_profile
    return render(request, 'user_profile.html', {'user_profile': user_profile})

@login_required(login_url=reverse_lazy('login'))
def vendor_changepassword(request,id):
    staff = get_object_or_404(Staff,pk=id)
    context ={
        'id':id,
        'staff':staff,
    }
    return render(request, 'vendor_changepassword.html', context)



@login_required(login_url=reverse_lazy('login'))
def vendor_changes_password(request, id):
    if request.method == 'POST':
        username = request.POST.get('username')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        print(username)
        user = authenticate(request, username=username, password=old_password)
        
        if user is not None:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()

                login(request, user)

                messages.success(request, 'Password changed successfully.')
                return redirect('login-provider') 

            else:
                messages.error(request, 'New passwords do not match.')
                
        else:
            messages.error(request, 'Invalid old password.')

    return render(request, 'vendor_changepassword.html', {'id': id})

@login_required(login_url=reverse_lazy('login'))
def submit_invoice(request, id):
    if request.method == 'POST':
        invoice_number = request.POST.get('invoiceNumber')
        staff_name=request.POST.get('staff_name')
        appointment_id = request.POST.get('appointment_id')  
        appointment = get_object_or_404(Appointment, pk=appointment_id)

        if invoice_number == appointment.invoice_number:
            appointment.dispute_created = True
            appointment.save()
            
            # Sending email to user
            subject = 'Dispute created successfully'
            message = 'Your dispute has been created successfully.'
            from_email = 'your_email@example.com'  
            to_email = appointment.user.email
            html_message = render_to_string('dispute_created.html', {'appointment': appointment})
            send_mail(subject, message, from_email, [to_email], fail_silently=False, html_message=html_message)
            staff_subject = 'Dispute recorded'
            staff_message = render_to_string('staff_dispute.html', {'appointment': appointment})    
            staff_member = Staff.objects.get(name=staff_name)
            staff_email = staff_member.email
            send_mail(staff_subject, strip_tags(staff_message), 'your_email@example.com', [staff_email], html_message=staff_message)                   
            messages.success(request, 'Dispute created successfully')
            print('Invoice Number Submitted:', invoice_number)
            return redirect('userPanel')
        else:
            messages.error(request, 'Invalid invoice number. Please try again.')

    return redirect('userPanel')


@login_required(login_url=reverse_lazy('login'))
def free_booking(request):
    user = request.user
    staff_id = request.POST.get('staff_id')
    email = request.POST.get('email')
    today = datetime.now().date()
    min_date = today.strftime('%Y-%m-%d')
    delta_time = today + timedelta(days=21)
    max_date = delta_time.strftime('%Y-%m-%d')
    day = request.session.get('day')
    number = request.session.get('number')
    service = request.session.get('service')
    address = request.session.get('address')
    time = request.session.get('time')
    email = request.session.get('email')
    latitude = request.session.get('latitude')
    longitude = request.session.get('longitude')
    description = request.session.get('description')

    if service == 'Plumber':
        staff_members = Staff.objects.filter(service='Plumber')
    elif service == 'Electrician':
        staff_members = Staff.objects.filter(service='Electrician')
    else:
        staff_members = Staff.objects.all()

    if request.method == 'POST':
        if service is not None and day <= max_date and day >= min_date:
            try:
                staff_member = Staff.objects.get(id=staff_id)
                invoice_number = generate_invoice_number()
                # Creating appointment for the selected staff member only
                appointment = Appointment.objects.create(
                    day=day,
                    time=time,
                    user=user,
                    address=address,
                    description=description,
                    number=number,
                    latitude=latitude,
                    longitude=longitude,
                    email=email,
                    service=service,
                    staff=staff_member.name,
                    payment_status='Free',  
                    invoice_number=invoice_number,
                )
                user_subject = 'New Appointment'
                user_message = render_to_string('user_appointment_created.html',
                                                 {'appointment': appointment})
                user_email = request.user.email
                send_mail(user_subject, strip_tags(user_message), 'your_email@example.com',
                          [user_email], html_message=user_message)

                staff_subject = 'New Appointment'
                staff_message = render_to_string('staff_appointment_created.html',
                                                  {'appointment': appointment})
                staff_email = staff_member.email
                send_mail(staff_subject, strip_tags(staff_message), 'your_email@example.com',
                          [staff_email], html_message=staff_message)

                messages.success(request, "Appointment created successfully!")
            except Staff.DoesNotExist:
                messages.error(request, "Selected staff member does not exist")

            return JsonResponse({'message': 'Appointment booked successfully'})
        else:
            messages.error(request, "The selected date isn't in the correct time period!")

    return render(request, 'userPanel.html', {'times': times})


