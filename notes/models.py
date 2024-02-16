from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# Create your models here.
class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    order = models.IntegerField()

    class Meta:
        verbose_name_plural = "branches"

    def __str__(self):
        return f"{self.code}: {self.name}"
    
class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    branch = models.ManyToManyField(Branch)
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])

    def __str__(self):
        return f"{self.code}: {self.name}"
    
class CourseModule(models.Model):
    number = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def calculateFiles(self):
        return File.objects.filter(course_module = self, approved = 1).count()

    no_of_files = property(calculateFiles)

    class Meta:
        verbose_name = "Module"

    def __str__(self):
        if self.number == 0:
            s = f"{self.course.code}"
        else:
            s = f"{self.course.code}-{self.number}"
        return f"{s}: {self.name}"
    
class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    file_url = models.URLField()
    file_name = models.CharField(max_length=200)
    file_extension = models.CharField(max_length=200)
    course_module = models.ForeignKey(CourseModule, on_delete=models.CASCADE)
    # 0 = pending, 1 = approved, 2 = duplicate, 3 = rejected
    approved = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    number_of_downloads = models.IntegerField(default=0)

    def __str__(self):
        if self.approved == 0:
            return f"{self.file_name[:10] + "..."} (pending)"
        return self.file_name
