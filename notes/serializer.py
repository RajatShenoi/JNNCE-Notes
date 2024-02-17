from rest_framework import serializers

from .models import Branch, Course, CourseModule

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'pk',
            'code',
            'name',
        )

class CourseModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseModule
        fields = (
            'pk',
            'name',
        )