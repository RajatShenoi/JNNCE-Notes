from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from notes.models import Branch, Course, CourseModule

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={
                'placeholder': 'Username',
                'autocomplete': 'off',
                'class': 'grow',
            }
        )
    )
    password = forms.CharField(
        max_length=150, widget=forms.PasswordInput(attrs={
                'placeholder': 'Password',
            }
        )
    )

class RegisterForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Username',
                'autocomplete': 'off',
                'class': 'grow',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'autocomplete': 'on',
                'class': 'grow',
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Password',
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': 'Confirm Password',
            }),
        }

class UploadFileForm(forms.Form):
    def __init__(self, course : Course, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.fields['module'] = forms.ModelChoiceField(
            queryset=CourseModule.objects.filter(course=course).order_by('number'),
            widget=forms.Select(attrs={
                    'class': 'select select-bordered',
                    'style': 'max-width: 90vw;',
                }
            )
        )
        self.fields['name'] = forms.CharField(
            max_length=100,
            widget=forms.TextInput(attrs={
                    'placeholder': 'File Name',
                    'autocomplete': 'off',
                    'style': 'max-width: 90vw;',
                    'class': 'grow',
                }
            )
        )
        self.fields['file'] = forms.FileField(
            allow_empty_file=False, 
            required=True,
            widget=forms.FileInput(attrs={
                    'class': 'file-input file-input-bordered',
                    'style': 'max-width: 90vw;',
                }
            )
        )
        
class ContributeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ContributeForm, self).__init__(*args, **kwargs)
        self.fields['branch'] = forms.ModelChoiceField(
            queryset=Branch.objects.all(),
            widget=forms.Select(attrs={
                    'class': 'select select-bordered',
                    'style': 'max-width: 90vw;',
                    'onchange': 'getCourseList(this.value);'
                }
            )
        )
        self.fields['course'] = forms.ModelChoiceField(
            queryset=Course.objects.none(),
            widget=forms.Select(attrs={
                    'class': 'select select-bordered',
                    'style': 'max-width: 90vw;',
                    'onchange': 'getModuleList(this.value);',
                }
            )
        )
        self.fields['module'] = forms.ModelChoiceField(
            queryset=CourseModule.objects.none(),
            widget=forms.Select(attrs={
                    'class': 'select select-bordered',
                    'style': 'max-width: 90vw;'
                }
            )
        )
        self.fields['name'] = forms.CharField(
            max_length=100,
            widget=forms.TextInput(attrs={
                    'placeholder': 'File Name',
                    'autocomplete': 'off',
                    'style': 'max-width: 90vw;',
                    'class': 'grow',
                }
            )
        )
        self.fields['file'] = forms.FileField(
            allow_empty_file=False, 
            required=True,
            widget=forms.FileInput(attrs={
                    'class': 'file-input file-input-bordered',
                    'style': 'max-width: 90vw;',
                }
            )
        )
        if 'branch' in self.data:
            try:
                branch_id = int(self.data.get('branch'))
                branch = Branch.objects.get(id=branch_id)
                self.fields['course'].queryset = Course.objects.filter(branch=branch).order_by('code')
            except (ValueError, TypeError, Branch.DoesNotExist):
                pass
        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                course = Course.objects.get(id=course_id)
                self.fields['module'].queryset = CourseModule.objects.filter(course=course).order_by('number')
            except (ValueError, TypeError, Course.DoesNotExist):
                pass