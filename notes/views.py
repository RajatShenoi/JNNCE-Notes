from django.http import Http404
from django.shortcuts import redirect, render
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required

from .forms import LoginForm, RegisterForm
from .models import Branch, Course, CourseModule


# Create your views here.
def home(request):
    branches = Branch.objects.all()

    return render(request, "notes/home.html", {
        "branches": branches,
    })

def displayCourseList(request, branch_code):
    branch = Branch.objects.get(code=branch_code)
    courses = Course.objects.filter(branch=branch)

    return render(request, "notes/course_list.html", {
        "branch": branch,
        "courses": courses,
    })

def displayModuleList(request, branch_code, course_code):
    branch = Branch.objects.get(code=branch_code)
    course = Course.objects.get(code=course_code)

    if course.branch != branch:
        raise Http404("Course not found in the specified branch")

    course_modules = CourseModule.objects.filter(course=course)

    return render(request, "notes/module_list.html", {
        "course": course,
        "course_modules": course_modules,
    })

def userRegister(request):
    if request.method == "GET":
        form = RegisterForm()
        return render(request, 'notes/register.html', {
            "form": form,
        })
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('notes:home')
        else:
            return render(request, 'notes/register.html', {
                "form": form,
            })
    
def userLogin(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'notes/login.html', {
            "form": form,
        })
    
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('notes:home')
            else:
                return render(request, 'notes/login.html', {
                    "form": form,
                })
        else:
            return render(request, 'notes/login.html', {
                "form": form,
            })

def userLogOut(request):
    logout(request)
    return redirect('notes:home')