# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def landing(request):
    # render your landing HTML (keeps design intact)
    return render(request, "accounts/landing.html")


def signup_view(request):
    # show form on GET, process on POST
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm_password", "")

        # Basic validation
        if not (first_name and last_name and email and password):
            messages.error(request, "Please fill all fields.")
            return redirect('accounts:signup')

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('accounts:signup')

        # Check if user with this email already exists
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "A user with that email already exists.")
            return redirect('accounts:signup')

        # Create the user. Use email as username for simplicity.
        user = User.objects.create_user(username=email, email=email, password=password,
                                        first_name=first_name, last_name=last_name)
        user.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('accounts:login')   # IMPORTANT: redirect to login page

    # GET
    return render(request, "accounts/signup.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        if not (email and password):
            messages.error(request, "Both email and password are required.")
            return redirect('accounts:login')

        # authenticate using username=email (we stored username=email in signup)
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:home')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('accounts:login')

    return render(request, "accounts/login.html")


@login_required(login_url='accounts:login')
def home(request):
    # user is request.user — show dynamic name
    return render(request, "accounts/dashboard.html", {"user": request.user})
