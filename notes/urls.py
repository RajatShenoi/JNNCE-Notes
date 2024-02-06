from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.home, name='home'),
    path('b/<str:branch_code>', views.displayCourseList, name='display-course-list'),
    path('b/<str:branch_code>/c/<str:course_code>', views.displayModuleList, name='display-module-list'),

    # authentication
    path('register', views.userRegister, name='register'),
    path('login', views.userLogin, name='login'),
    path('logout', views.userLogOut, name='logout'),
]