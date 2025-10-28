from datetime import timedelta, timezone
import uuid
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import secrets
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


def home(request):
    # Your code logic goes here
    context = {
        'message': 'Hello, world!'
    }
    return render(request, 'index.html', context)

def about_view(request):
    return render(request, 'about.html')

def services_view(request):
    return render(request, 'services.html')

def contact_view(request):
    return render(request, 'contact.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if username and email and password:
            # Check if the email is already registered
            if User.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered. Please use a different email.")
                return redirect('register')

            # Check if the username is already taken
            if User.objects.filter(username=username).exists():
                messages.error(request, "This username is already taken. Please choose a different username.")
                return redirect('register')

            try:
                user = User.objects.create_user(username, email, password)
                user.is_active = False
                user.save()

                # Determine the protocol based on the request
                protocol = 'https' if request.is_secure() else 'http'

                # Send email verification
                current_site = get_current_site(request)
                subject = 'Activate Your Account'
                message = render_to_string('activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'protocol': protocol,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                
                # Fixed: Don't overwrite the email variable
                user_email = email  # Store original email
                email_message = EmailMessage(subject, message, to=[user_email])
                email_message.content_subtype = "html"
                email_message.send()

                messages.success(request, 'Please check your email to activate your account.')
                return redirect('register')
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect('register')
        else:
            messages.error(request, "Please fill in all the required fields.")
            return redirect('register')
    elif request.method == 'GET':
        return render(request, 'register.html')
    else:
        return HttpResponse("Method Not Allowed", status=405)


def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)  # Use the custom User model
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated. Please login.")
        return redirect('login')  
    else:
        messages.error(request, "Invalid Link. Please try again or contact support.")
        return redirect('register')



def loginn(request):
    return render(request, 'choose_login.html')

def login_view(request):
    if request.method == 'GET':
        # Add the logic for handling the GET request
        return render(request, 'login.html')
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if a user with the provided email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is not None:
            if not user.is_active:
                # If the account is not activated, show an error message
                messages.error(request, "Your account is not activated. Please activate your account.")
                return redirect('login')  # Redirect back to the login page

            # If the user exists and is active, attempt authentication using the email and password
            authenticated_user = authenticate(request, username=user.username, password=password)
            
            if authenticated_user is not None:
                # Check if the authenticated user is active
                if authenticated_user.is_active:
                    login(request, authenticated_user)                    
                    messages.success(request, "You have been logged in successfully!")
                    return redirect('booking')  # Redirect to the home page after successful login
                else:
                    messages.error(request, "Your account is not activated. Please activate your account.")
                    return redirect('login')  # Redirect back to the login page
            else:
                messages.error(request, "Invalid email or password. Please try again.")
                return redirect('login')  # Redirect back to the login page if the authentication fails
        else:
            messages.error(request, "User with the provided email does not exist. Please try again.")
            return redirect('login')  # Redirect back to the login page if the user does not exist
    else:
        return HttpResponse("Method Not Allowed", status=405)
 


# def forgot_password_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         try:
#             user = User.objects.get(email=email)
#             request.session['reset_email'] = user.email  # Store the email in the session
#             messages.success(request, "Please proceed to change your password.")
#             return redirect('change_password')  # Redirect to the password change view
#         except User.DoesNotExist:
#             messages.error(request, "User with the provided email does not exist. Please try again.")
#             return redirect('forgot_password')
#     else:
#         return render(request, 'forgot.html')


# # Change Password View
# def change_password(request):
#     if request.method == 'POST':
#         new_password = request.POST.get('new_password')
#         confirm_password = request.POST.get('confirm_password')

#         # Retrieve the email from the session
#         reset_email = request.session.get('reset_email')
#         if not reset_email:
#             messages.error(request, "No password reset request found.")
#             return redirect('forgot_password')

#         if new_password != confirm_password:
#             messages.error(request, 'The two password fields didn’t match.')
#             return render(request, 'reset.html')
#         try:
#             user = User.objects.get(email=reset_email)
#             user.set_password(new_password)
#             user.save()
#             update_session_auth_hash(request, user)  # Keep the user logged in after password change
#             messages.success(request, 'Your password was successfully updated!')
#             return redirect('login')  # Redirect to login page
#         except User.DoesNotExist:
#             messages.error(request, "User not found.")
#             return redirect('forgot_password')
#     else:
#         return render(request, 'reset.html')
#faq
def faq_view(request):
    return render(request, 'faq.html')
    

def logout_view(request):
    logout(request)
    # Optionally, you can add a success message here
    return redirect('login') 



def forgot_password_view(request):
    if request.method == 'POST':
        
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                # If the account is not activated, show an error message
                messages.error(request, "Your account is not activated. Please activate your account.")
                return redirect('login')  # Redirect back to the login page
            request.session['reset_email'] = user.email  
            
            # Send verification email
            verification_token = generate_verification_token()
            request.session['verification_token'] = verification_token  
            user.verification_token = verification_token
            user.save()

            subject = "Password Reset Verification"
            message = render_to_string('password_reset_verify.html', {'user': user,
                'reset_token': verification_token,
            })
            plain_message = strip_tags(message)

            send_mail(
                subject,
                plain_message,
                'sewaghar93@gmail.com',  # Replace with your sender email
                [user.email],
                html_message=message,
            )
            print("Reset Email in Session:", request.session.get('reset_email'))
            print("Verification Token in Session:", request.session.get('verification_token'))
            return redirect('verification')  
        except User.DoesNotExist:
            messages.error(request, "User with the provided email does not exist. Please try again.")
            return redirect('login')
    else:
        return render(request, 'forgot.html')


def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        reset_email = request.session.get('reset_email')
        if not reset_email:
            messages.error(request, "No password reset request found.")
            return redirect('forgot_password')

        if new_password != confirm_password:
            messages.error(request, 'The two password fields didn’t match.')
            return render(request, 'reset.html')
        
        try:
            user = User.objects.get(email=reset_email)
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('login')  # Redirect to login page
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('forgot_password')
    else:
        return render(request, 'reset.html')



def generate_verification_token():
    # Generate a 12-character random token using secrets module
    return secrets.token_hex(6)

def verification(request):
    if request.method == 'GET':
        reset_email = request.session.get('reset_email')
        saved_token = request.session.get('verification_token')
        
        if not reset_email or not saved_token:
            messages.error(request, "Incorrect Verification Token")
            return redirect('login') 
        
        return render(request, 'verification.html')
    
    elif request.method == 'POST':
        entered_token = request.POST.get('entered_token')
        saved_token = request.session.get('verification_token')

        if entered_token == saved_token:
            messages.success(request, "Verification Token matched. Please proceed to reset password")
            return render(request, 'reset.html')  # Redirect to reset.html upon successful token verification
        else:
            messages.error(request, "Invalid verification token.")
            return render(request, 'login.html', {'show_swal_alert': True})



def contact_form(request):
    if request.method == 'POST':
        # Process form data here
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        message = request.POST.get('message')
        subject = 'Thank you for contacting us. '
        html_message = render_to_string('contact_email.html', {'name': name})
        plain_text_message = strip_tags(html_message)
        from_email = 'sewaghar93@gmail.com'
        to_email = [email]
        send_mail(subject, plain_text_message, from_email, to_email, html_message=html_message, fail_silently=False)        
        subject = f'New contact form submission from {name}'
        sewa_html_message = render_to_string('contact_email_sewa.html', {'name': name, 'phone_number': phone_number, 'email': email, 'message': message})
        sewa_plain_text_message = strip_tags(sewa_html_message)
        sewa_from_email = 'sewaghar93@gmail.com'
        sewa_to_email = ['sewaghar93@gmail.com']
        send_mail(subject, sewa_plain_text_message, sewa_from_email, sewa_to_email, html_message=sewa_html_message, fail_silently=False)

    return render(request, 'index.html')

