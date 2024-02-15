import mimetypes
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required

from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError
from django.urls import reverse
from notes.azure_file_controller import delete_blob, download_blob, upload_file_to_blob
from notes.exceptions import NotAllowedExtenstionError, UploadBlobError

from .forms import LoginForm, RegisterForm, UploadFileForm
from .models import Branch, Course, CourseModule, File


# Create your views here.
def home(request):
    branches = Branch.objects.all()

    return render(request, "notes/home.html", {
        "branches": branches,
    })

def displayCourseList(request, branch_code):
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
        },
        "current": f"{branch_code}",
    }
    try:
        branch = Branch.objects.get(code=branch_code)
    except Branch.DoesNotExist:
        raise Http404
    
    courses = Course.objects.filter(branch=branch)

    return render(request, "notes/course_list.html", {
        "branch": branch,
        "courses": courses,
        "crumbs": crumbs,
    })

def displayModuleList(request, branch_code, course_code):
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
            f"{branch_code}": reverse("notes:display-course-list", args=[branch_code]),
        },
        "current": f"{course_code}",
    }
    try:
        branch = Branch.objects.get(code=branch_code)
        course = Course.objects.get(code=course_code)
    except (Branch.DoesNotExist, Course.DoesNotExist):
        raise Http404

    if course.branch != branch:
        raise Http404

    course_modules = CourseModule.objects.filter(course=course)

    return render(request, "notes/module_list.html", {
        "branch": branch,
        "course": course,
        "course_modules": course_modules,
        "crumbs": crumbs,
    })

def displayFileList(request, branch_code, course_code, pk):
    try:
        branch = Branch.objects.get(code=branch_code)
        course = Course.objects.get(code=course_code)
        course_module = CourseModule.objects.get(pk=pk)
    except (Branch.DoesNotExist, Course.DoesNotExist, CourseModule.DoesNotExist):
        raise Http404

    if course.branch != branch:
        raise Http404

    if course_module.course != course:
        raise Http404

    files = File.objects.filter(course_module=course_module, approved=1).order_by('-date_created')

    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
            f"{branch_code}": reverse("notes:display-course-list", args=[branch_code]),
            f"{course_code}": reverse("notes:display-module-list", args=[branch_code, course_code])
        },
        "current": f"{course_module.name}",
    }

    return render(request, "notes/file_list.html", {
        "course": course,
        "course_module": course_module,
        "files": files,
        "crumbs": crumbs,
    })

def userRegister(request):
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
        },
        "current": "Register",
    }
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('notes:home')
        else:
            for error in form.errors:
                messages.error(request, f"{error}: {form.errors[error][0]}")
            return render(request, 'notes/register.html', {
                "form": form,
                "crumbs": crumbs,
            })
        
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in")
        return redirect('notes:home')
    form = RegisterForm()
    return render(request, 'notes/register.html', {
        "form": form,
        "crumbs": crumbs,
    })
    
def userLogin(request):
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
        },
        "current": "Login",
    }

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next = request.GET.get('next')
                if next:
                    return redirect(next)
                return redirect('notes:home')
            else:
                messages.error(request, "Invalid username or password")
                return render(request, 'notes/login.html', {
                    "form": form,
                    "crumbs": crumbs,
                })
        else:
            for error in form.errors:
                messages.error(request, f"{error}: {form.errors[error][0]}")
            return render(request, 'notes/login.html', {
                "form": form,
            })
    
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in")
        return redirect('notes:home')
    form = LoginForm()
    return render(request, 'notes/login.html', {
        "form": form,
        "crumbs": crumbs,
    })

def userLogOut(request):
    logout(request)
    return redirect('notes:home')

# @login_required
def uploadFile(request, course_code):
    try:
        course = Course.objects.get(code=course_code)
    except Course.DoesNotExist:
        raise Http404
    
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
            f"{course.branch.code}": reverse("notes:display-course-list", args=[course.branch.code]),
        },
        "current": "Contribute",
    }
    
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
                    "crumbs": crumbs,
                })
            course_module = form.cleaned_data['module']
            
            try:
                file_object = upload_file_to_blob(
                    file,
                    display_name,
                    request.user,
                    course_module,
                )
            except ClientAuthenticationError as e:
                messages.error(request, f"{e.error}: {e.message}. Contact admin.")
                return render(request, 'notes/upload.html', {
                    "form": form,
                    "course": course,
                    "crumbs": crumbs,
                })
            except ResourceNotFoundError as e:
                messages.error(request, f"{e.error}: {e.message}. Contact admin.")
                return render(request, 'notes/upload.html', {
                    "form": form,
                    "course": course,
                    "crumbs": crumbs,
                })
            except UploadBlobError:
                messages.error(request, "File upload failed. Contact admin.")
                return render(request, 'notes/upload.html', {
                    "form": form,
                    "course": course,
                    "crumbs": crumbs,
                })
            except NotAllowedExtenstionError:
                messages.error(request, "File type not allowed. Only .pdf files are allowed.")
                return render(request, 'notes/upload.html', {
                    "form": form,
                    "course": course,
                    "crumbs": crumbs,
                })
            else:
                if file_object is None:
                    messages.error(request, "File upload failed")
                    return render(request, 'notes/upload.html', {
                        "form": form,
                        "course": course,
                        "crumbs": crumbs,
                    })
            messages.success(request, "File uploaded successfully. A moderator will need to approve the file before it is made public.")
            return redirect('notes:contributions')
        else:
            messages.error(request, "Invalid form")
            return render(request, 'notes/upload.html', {
                "form": form,
                "course": course,
                "crumbs": crumbs,
            })
    form = UploadFileForm(course)
    return render(request, 'notes/upload.html', {
        "form": form,
        "course": course,
        "crumbs": crumbs,
    })

def downloadFile(request, pk):
    try:
        file = File.objects.get(pk=pk)
    except File.DoesNotExist:
        raise Http404
    
    if request.user != file.user and file.approved != 1:
        raise Http404
    elif request.user == file.user and file.approved != 1:
        messages.error(request, "File can be downloaded only after it has been approved.")
        return redirect('notes:contributions')

    file_name = f"{file.file_name}{file.file_extension}"
    file_type, _ = mimetypes.guess_type(file_name)
    url = file.file_url
    blob_name = url.split("/")[-1]
    try:
        blob_content = download_blob(blob_name)
    except ClientAuthenticationError as e:
        messages.error(request, f"{e.error}: {e.message}. Contact admin.")
        return redirect('notes:contributions')
    except ResourceNotFoundError as e:
        messages.error(request, f"{e.error}: {e.message}. Contact admin.")
        return redirect('notes:contributions')
    if blob_content:
        response = HttpResponse(blob_content.readall(), content_type=file_type)
        response['Content-Disposition'] = f'inline; filename={file_name}'
        return response
    return Http404

@login_required
def contributions(request):
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
        },
        "current": "My Contributions",
    }
    files = File.objects.filter(user=request.user).order_by('-date_created')

    if len(files) == 0:
        messages.info(request, "You have not contributed any files yet.")
    
    return render(request, "notes/contributions.html", {
        "files": files,
        "crumbs": crumbs,
    })

@login_required
def deleteFile(request, pk):
    try:
        file = File.objects.get(pk=pk)
    except File.DoesNotExist:
        raise Http404
    
    if file.user != request.user:
        messages.error(request, "You are not authorized to delete this file")
        return redirect('notes:contributions')
    
    if file.approved == 1:
        messages.error(request, "File cannot be deleted once it has been approved. Please contact the admin.")
        return redirect('notes:contributions')
    
    try:
        delete_blob(file.file_url.split("/")[-1])
        file.delete()
    except ClientAuthenticationError as e:
        messages.error(request, f"{e.error}: {e.message}. Contact admin.")
        return redirect('notes:contributions')
    except ResourceNotFoundError as e:
        messages.error(request, f"{e.error}: {e.message}. Contact admin.")
        return redirect('notes:contributions')
    
    return redirect('notes:contributions')