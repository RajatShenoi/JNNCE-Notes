from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from notes.models import Course, CourseModule

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={
                'placeholder': 'Username',
                'class': 'grow-0',
                'autocomplete': 'off',
            }
        )
    )
    password = forms.CharField(
        max_length=150, widget=forms.PasswordInput(attrs={
                'placeholder': 'Password',
                'class': 'grow-0',
            }
        )
    )

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UploadFileForm(forms.Form):
    def __init__(self, course : Course, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.fields['module'] = forms.ModelChoiceField(queryset=CourseModule.objects.filter(course=course).order_by('number'))
        self.fields['name'] = forms.CharField(max_length=100)
        self.fields['file'] = forms.FileField()
        