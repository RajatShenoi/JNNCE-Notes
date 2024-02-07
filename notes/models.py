from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# Create your models here.
class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "branches"

    def __str__(self):
        return f"{self.code}: {self.name}"
    
class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])

    def __str__(self):
        return f"{self.branch.code}-{self.code}: {self.name}"
    
class CourseModule(models.Model):
    number = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Module"

    def __str__(self):
        if self.number == 0:
            s = f"{self.course.code}"
        else:
            s = f"{self.course.code}-{self.number}"
        return f"{self.course.branch.code}-{s}: {self.name}"
    
class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    file_url = models.URLField()
    file_name = models.CharField(max_length=200)
    file_extension = models.CharField(max_length=200)
    course_module = models.ForeignKey(CourseModule, on_delete=models.CASCADE)
    # 0 = pending, 1 = approved, 2 = duplicate, 3 = rejected
    approved = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.file_name
