from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required

from notes.models import Branch, Course, CourseModule, File

admin.site.login = staff_member_required(admin.site.login, login_url=settings.LOGIN_URL)

# Register your models here.
admin.site.register(Branch)
admin.site.register(Course)
admin.site.register(CourseModule)
admin.site.register(File)