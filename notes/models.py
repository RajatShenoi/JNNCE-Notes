from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
        return f"{self.course.branch.code}-{self.course.code}-{self.number}: {self.name}"
    
class File(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    file_url = models.URLField(null=True)
    file_name = models.CharField(max_length=200, null=True)
    file_extension = models.CharField(max_length=200, null=True)
    course_module = models.ForeignKey(CourseModule, on_delete=models.CASCADE)
    deleted = models.BooleanField(null=True, default=False)

    def __str__(self):
        return self.file_name
