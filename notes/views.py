from django.http import Http404
from django.shortcuts import render
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
    if branch is None:
        return Http404("Branch does not exist")
    course = Course.objects.get(code=course_code)
    course_modules = CourseModule.objects.filter(course=course)

    return render(request, "notes/module_list.html", {
        "course": course,
        "course_modules": course_modules,
    })