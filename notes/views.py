import mimetypes
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required

from pathlib import Path

from notes.azure_file_controller import download_blob, upload_file_to_blob

from .forms import LoginForm, RegisterForm, UploadFileForm
from .models import Branch, Course, CourseModule, File


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
        "branch": branch,
        "course": course,
        "course_modules": course_modules,
    })

def displayFileList(request, branch_code, course_code, pk):
    branch = Branch.objects.get(code=branch_code)
    course = Course.objects.get(code=course_code)
    course_module = CourseModule.objects.get(pk=pk)

    if course.branch != branch:
        raise Http404("Course not found in the specified branch")

    if course_module.course != course:
        raise Http404("Module not found in the specified course")

    files = File.objects.filter(course_module=course_module, approved=True, deleted=False).order_by('-date_created')

    return render(request, "notes/file_list.html", {
        "course": course,
        "course_module": course_module,
        "files": files,
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

@login_required
def uploadFile(request, course_code):
    course = Course.objects.get(code=course_code)
    course_modules = CourseModule.objects.filter(course=course).order_by('number')
    if request.method == "POST":
        form = UploadFileForm(course, request.POST, request.FILES)
        if form.is_valid():
            display_name = form.cleaned_data['name']
            file = form.cleaned_data['file']
            if file.size > 5242880:
                messages.error(request, "You cannot upload file more than 5Mb")
                return render(request, 'notes/upload.html', {
                    "form": form,
                    "course": course,
                })
            course_module = form.cleaned_data['module']

            file_object = upload_file_to_blob(
                file,
                display_name,
                request.user,
                course_module,
            )

            if file_object is None:
                messages.error(request, "File upload failed")
                return render(request, 'notes/upload.html', {
                    "form": form,
                    "course": course,
                })
            # TODO
            # To be redirected to the files upload page.
            return redirect('notes:home')
        else:
            # TODO
            pass
    form = UploadFileForm(course)
    return render(request, 'notes/upload.html', {
        "form": form,
        "course": course,
    })

def downloadFile(request, pk):
    file = File.objects.get(pk=pk)
    file_name = f"{file.file_name}{file.file_extension}"
    file_type, _ = mimetypes.guess_type(file_name)
    url = file.file_url
    blob_name = url.split("/")[-1]
    blob_content = download_blob(blob_name)
    if blob_content:
        response = HttpResponse(blob_content.readall(), content_type=file_type)
        response['Content-Disposition'] = f'inline; filename={file_name}'
        return response
    return Http404

@login_required
def contributions(request):
    files = File.objects.filter(user=request.user).order_by('-date_created')

    return render(request, "notes/contributions.html", {
        "files": files,
    })