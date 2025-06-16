import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout


def welcome(request):
    return render(request, 'welcome.html')

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'User with this username already exists')
            return redirect('/auth/register/')

        otp = random.randint(100000, 999999)

        # Save in session
        request.session['register_data'] = {
            'username': username,
            'email': email,
            'password': password,
            'otp': str(otp),
        }
        request.session.modified = True
        request.session.set_expiry(300)  # Optional: expires in 5 minutes

        try:
            send_mail(
                'Your DeepLogic OTP',
                f'Your OTP for DeepLogic registration is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            messages.error(request, f"Error sending OTP: {str(e)}")
            return redirect('/auth/register/')

        messages.success(request, 'OTP sent to your email.')
        return redirect('/auth/verify_otp/')

    return render(request, 'register.html')


def verify_otp(request):
    temp_user = request.session.get('register_data')
    if not temp_user:
        messages.error(request, "Session expired. Please register again.")
        return redirect('/auth/register/')

    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        if input_otp == temp_user['otp']:
            user = User.objects.create_user(
                username=temp_user['username'],
                email=temp_user['email']
            )
            user.set_password(temp_user['password'])
            user.save()

            del request.session['register_data']
            messages.success(request, "Registration successful. Please login.")
            return redirect('/auth/login/')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'verify_otp.html')


    

def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.info(request, 'User with this username does not exist')
            return redirect('/auth/login/')

        user = authenticate(username=username, password=password)

        if user is None:
            messages.info(request, 'Invalid password')
            return redirect('/auth/login/')

        login(request, user)
        messages.info(request, 'Login successful')

        return redirect('/submit/profile/')  # Redirect to profile page after login

    template = loader.get_template('login.html')
    context = {}
    return HttpResponse(template.render(context, request))


def logout_user(request):
    logout(request)
    messages.info(request, 'Logout successful')
    return redirect('/auth/login/')