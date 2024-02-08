from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.home, name='home'),
    path('b/<str:branch_code>', views.displayCourseList, name='display-course-list'),
    path('b/<str:branch_code>/c/<str:course_code>', views.displayModuleList, name='display-module-list'),
    path('b/<str:branch_code>/c/<str:course_code>/m/<str:pk>', views.displayFileList, name='display-file-list'),

    path('my-contributions', views.contributions, name='contributions'),

    # azure blob storage
    path('upload/<str:course_code>', views.uploadFile, name='upload-file'),
    path('download/<str:pk>', views.downloadFile, name='download-file'),
    path('delete/<str:pk>', views.deleteFile, name='delete-file'),

    # authentication
    path('register', views.userRegister, name='register'),
    path('login', views.userLogin, name='login'),
    path('logout', views.userLogOut, name='logout'),
]