import mimetypes

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin

from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError
from django.urls import reverse, reverse_lazy

from notes.azure_file_controller import delete_blob, download_blob, upload_file_to_blob
from notes.exceptions import NotAllowedExtenstionError, UploadBlobError
from notes.serializer import CourseModuleSerializer, CourseSerializer

from verify_email.email_handler import send_verification_email

from .forms import ContributeForm, LoginForm, RegisterForm, UploadFileForm
from .models import Branch, Course, CourseModule, File


# Create your views here.
def home(request):
    return render(request, "notes/home.html", {
       
    })

def resources(request):
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
        },
        "current": "Resources",
    }
    branches = Branch.objects.all().order_by('order')
    return render(request, "notes/resources.html", {
        "crumbs": crumbs,
        "branches": branches,
    })

def displayCourseList(request, branch_code):
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
            "Resources": reverse("notes:resources"),
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
            "Resources": reverse("notes:resources"),
            f"{branch_code}": reverse("notes:display-course-list", args=[branch_code]),
        },
        "current": f"{course_code}",
    }
    try:
        branch = Branch.objects.get(code=branch_code)
        course = Course.objects.get(code=course_code)
    except (Branch.DoesNotExist, Course.DoesNotExist):
        raise Http404

    if branch not in course.branch.all():
        raise Http404

    course_modules = CourseModule.objects.filter(course=course).order_by('number')

    count = {}
    for module in course_modules:
        count[str(module)] = File.objects.filter(course_module = module, approved = 1).count()

    return render(request, "notes/module_list.html", {
        "branch": branch,
        "course": course,
        "course_modules": course_modules,
        "crumbs": crumbs,
        "count": count,
    })

def displayFileList(request, branch_code, course_code, pk):
    try:
        branch = Branch.objects.get(code=branch_code)
        course = Course.objects.get(code=course_code)
        course_module = CourseModule.objects.get(pk=pk)
    except (Branch.DoesNotExist, Course.DoesNotExist, CourseModule.DoesNotExist):
        raise Http404

    if branch not in course.branch.all():
        raise Http404

    if course_module.course != course:
        raise Http404

    files = File.objects.filter(course_module=course_module, approved=1).order_by('-date_created')

    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
            "Resources": reverse("notes:resources"),
            f"{branch_code}": reverse("notes:display-course-list", args=[branch_code]),
            f"{course_code}": reverse("notes:display-module-list", args=[branch_code, course_code])
        },
        "current": f"{course_module.name}",
    }

    return render(request, "notes/file_list.html", {
        "branch": branch,
        "course": course,
        "course_module": course_module,
        "files": files,
        "crumbs": crumbs,
    })

def userRegister(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in")
        return redirect('notes:home')
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
        },
        "current": "Register",
    }
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                try:
                    user = User.objects.get(email=form.cleaned_data['email'])
                    messages.error(request, "User with this email already exists")
                    return render(request, 'notes/register.html', {
                        "form": form,
                        "crumbs": crumbs,
                    })
                except User.DoesNotExist:
                    user = send_verification_email(request, form)
                    user.username = user.username.lower()
                    user.save()
                    messages.success(request, f"Account created successfully for {user.email}. Kindly check your email for a verification link.")
                    return redirect('notes:home')
            except Exception as e:
                messages.error(request, f"There was an error. Contact us with:  Error: {e}")
                return render(request, 'notes/register.html', {
                    "form": form,
                    "crumbs": crumbs,
                })
        else:
            for error in form.errors:
                messages.error(request, f"{error}: {form.errors[error][0]}")
            return render(request, 'notes/register.html', {
                "form": form,
                "crumbs": crumbs,
            })
        
    form = RegisterForm()
    return render(request, 'notes/register.html', {
        "form": form,
        "crumbs": crumbs,
    })
    
def userLogin(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in")
        return redirect('notes:home')
    
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
        },
        "current": "Login",
    }

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].lower()
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next = request.GET.get('next')
                if next:
                    return redirect(next)
                return redirect('notes:home')
            else:
                temp_user = User.objects.filter(username=username)
                if temp_user.exists():
                    temp_user = temp_user.first()
                    if temp_user.is_active == False:
                        messages.warning(request, "Account not verified. A verification link was sent earlier. Kindly check your email.")
                        return render(request, 'notes/login.html', {
                            "form": form,
                            "crumbs": crumbs,
                        })
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
    
    form = LoginForm()
    return render(request, 'notes/login.html', {
        "form": form,
        "crumbs": crumbs,
    })

def userLogOut(request):
    logout(request)
    return redirect('notes:home')

@login_required
def contribute(request):
    if request.method == "POST":
        form = ContributeForm(request.POST, request.FILES)
        if form.is_valid():
            display_name = form.cleaned_data['name']
            file = form.cleaned_data['file']
            if file.size > 5242880:
                messages.error(request, "You cannot upload file more than 5Mb")
                return render(request, 'notes/contribute.html', {
                    "form": form,
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
                return render(request, 'notes/contribute.html', {
                    "form": form,
                })
            except ResourceNotFoundError as e:
                messages.error(request, f"{e.error}: {e.message}. Contact admin.")
                return render(request, 'notes/contribute.html', {
                    "form": form,
                })
            except UploadBlobError:
                messages.error(request, "File upload failed. Contact admin.")
                return render(request, 'notes/contribute.html', {
                    "form": form,
                })
            except NotAllowedExtenstionError:
                messages.error(request, "File type not allowed. Only .pdf files are allowed.")
                return render(request, 'notes/contribute.html', {
                    "form": form,
                })
            else:
                if file_object is None:
                    messages.error(request, "File upload failed")
                    return render(request, 'notes/contribute.html', {
                        "form": form,
                    })
            messages.success(request, "Thank you for contributing! A moderator will need to approve the file before it is made public.")
            return redirect('notes:contributions')
        else:
            print(form.errors)

    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
        },
        "current": "Contribute",
    }
    form = ContributeForm()
    return render(request, 'notes/contribute.html', {
        "crumbs": crumbs,
        "form": form,
    })

@login_required
def uploadFile(request, branch_code, course_code):
    try:
        branch = Branch.objects.get(code=branch_code)
        course = Course.objects.get(code=course_code)
    except Course.DoesNotExist:
        raise Http404
    
    if branch not in course.branch.all():
        raise Http404
    
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
            "Resources": reverse("notes:resources"),
            f"{branch.code}": reverse("notes:display-course-list", args=[branch.code]),
            f"{course.code}": reverse("notes:display-module-list", args=[branch.code, course.code]),
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
            messages.success(request, "Thank you for contributing! A moderator will need to approve the file before it is made public.")
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
        file.number_of_downloads += 1
        file.save()
        response = HttpResponse(blob_content.readall(), content_type=file_type)
        response['Content-Disposition'] = f'inline; filename={file_name.replace(",", "")}'
        return response
    return Http404

@login_required
def contributions(request):
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
        },
        "current": f"My Contributions - @{request.user.username}",
    }
    files = File.objects.filter(user=request.user).order_by('-date_created')

    if len(files) == 0:
        messages.info(request, "You have not contributed any files yet.")
    
    return render(request, "notes/contributions.html", {
        "files": files,
        "crumbs": crumbs,
    })

def topContributors(request):
    crumbs = {
        "path": {
            "Home": reverse("notes:home"),
        },
        "current": "Top Contributors",
    }
    
    contrib = {}
    for user in User.objects.all():
        count = File.objects.filter(user=user, approved=1).count()
        if count > 0:
            contrib[user.username] = count

    contrib = dict(sorted(contrib.items(), key=lambda item: item[1], reverse=True))

    return render(request, "notes/top_contributors.html", {
        "crumbs": crumbs,
        "contrib": contrib,
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

def apiGetCourses(request, branch_id):
    try:
        branch = Branch.objects.get(pk=branch_id)
    except Branch.DoesNotExist:
        raise Http404
    
    courses = Course.objects.filter(branch=branch)
    serializer = CourseSerializer(courses, many=True)
    return JsonResponse(serializer.data, safe=False)

def apiGetModules(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        raise Http404
    
    course_modules = CourseModule.objects.filter(course=course)
    serializer = CourseModuleSerializer(course_modules, many=True)
    return JsonResponse(serializer.data, safe=False)

class ResetPasswordView(UserPassesTestMixin, SuccessMessageMixin, PasswordResetView):
    template_name = 'notes/password_reset/password_reset.html'
    email_template_name = 'notes/password_reset/password_reset_email.html'
    html_email_template_name = 'notes/password_reset/password_reset_email.html'
    subject_template_name = 'notes/password_reset/password_reset_subject.html'
    
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."

    success_url = reverse_lazy('notes:login')

    def handle_no_permission(self):
        messages.info(self.request, "You are already logged in")
        return redirect('notes:home')

    def test_func(self):
        return self.request.user.is_anonymous
    
class ResetPasswordConfirmView(UserPassesTestMixin, SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'notes/password_reset/password_reset_confirm.html'
    success_message = "Your password has been reset. You may login with the new password."

    success_url = reverse_lazy('notes:login')

    def handle_no_permission(self):
        messages.info(self.request, "You are already logged in")
        return redirect('notes:home')

    def test_func(self):
        return self.request.user.is_anonymous