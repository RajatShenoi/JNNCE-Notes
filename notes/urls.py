from django.urls import path

from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.home, name='home'),
    path('resources/', views.resources, name='resources'),
    path('resources/b/<str:branch_code>/', views.displayCourseList, name='display-course-list'),
    path('resources/b/<str:branch_code>/c/<str:course_code>/', views.displayModuleList, name='display-module-list'),
    path('resources/b/<str:branch_code>/c/<str:course_code>/m/<str:pk>/', views.displayFileList, name='display-file-list'),

    path('top-contributors/', views.topContributors, name='top-contributors'),
    path('my-contributions/', views.contributions, name='contributions'),
    path('contribute/', views.contribute, name='contribute'),

    path('contact/', views.contact, name='contact'),

    # azure blob storage
    path('resources/contribute/<str:branch_code>/<str:course_code>/', views.uploadFile, name='upload-file'),
    path('resources/download/<str:pk>/', views.downloadFile, name='download-file'),
    path('resources/delete/<str:pk>/', views.deleteFile, name='delete-file'),

    # api
    path('api/getCourses/<int:branch_id>/', views.apiGetCourses, name='api-get-courses'),
    path('api/getModules/<int:course_id>/', views.apiGetModules, name='api-get-modules'),
]