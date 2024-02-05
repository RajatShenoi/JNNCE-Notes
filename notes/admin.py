from django.contrib import admin

from notes.models import Branch, Course, CourseModule

# Register your models here.
admin.site.register(Branch)
admin.site.register(Course)
admin.site.register(CourseModule)