from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Signup
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully ✅")
            return redirect('login')
        else:
            messages.error(request, "Please fix the errors below ❌")

    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


# Login
def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful 🎉")
            return redirect('profile')
        else:
            messages.error(request, "Invalid username or password ❌")

    return render(request, 'login.html')


# Profile
@login_required(login_url='login')
def profile(request):
    return render(request, 'profile.html')


# Logout
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully 👋")
    return redirect('login')