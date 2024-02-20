from django import forms

from notes.models import Branch, Course, CourseModule

from allauth.account.forms import LoginForm, SignupForm, ReauthenticateForm, ResetPasswordForm, AddEmailForm, SetPasswordForm

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

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget.attrs['class'] = 'grow'
        self.fields['login'].widget.attrs['style'] = 'max-width: 90vw;'
        self.fields['login'].widget.attrs['autocomplete'] = 'off'
        self.fields['password'].widget.attrs['class'] = 'grow'
        self.fields['password'].widget.attrs['style'] = 'max-width: 90vw;'
        self.fields['password'].widget.attrs['autocomplete'] = 'off'
        self.fields['remember'].widget.attrs['class'] = 'checkbox checkbox-success'
    
class CustomSignUpForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignUpForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(
            widget=forms.EmailInput(attrs={
                'placeholder': 'Email address',
                'autocomplete': 'off',
                'class': 'grow',
                'style': 'max-width: 90vw;',
            })
        )

        self.fields['username'].widget.attrs['class'] = 'grow'
        self.fields['username'].widget.attrs['autocomplete'] = 'off'

        self.fields['password1'].widget.attrs['class'] = 'grow'
        self.fields['password1'].widget.attrs['style'] = 'max-width: 90vw;'
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'

        self.fields['password2'].widget.attrs['class'] = 'grow'
        self.fields['password2'].widget.attrs['style'] = 'max-width: 90vw;'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['style'] = 'max-width: 90vw;'

class CustomReauthenticateForm(ReauthenticateForm):
    def __init__(self, *args, **kwargs):
        super(CustomReauthenticateForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget.attrs['class'] = 'grow'
        self.fields['password'].widget.attrs['style'] = 'max-width: 90vw;'
        self.fields['password'].widget.attrs['autocomplete'] = 'off'

class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(
            widget=forms.EmailInput(attrs={
                'placeholder': 'Email address',
                'autocomplete': 'off',
                'class': 'grow',
                'style': 'max-width: 90vw;',
            })
        )

class CustomAddEmailForm(AddEmailForm):
    def __init__(self, *args, **kwargs):
        super(CustomAddEmailForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(
            widget=forms.EmailInput(attrs={
                'placeholder': 'Email address',
                'autocomplete': 'off',
                'class': 'grow',
                'style': 'max-width: 90vw;',
            })
        )

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'grow'
        self.fields['password1'].widget.attrs['style'] = 'max-width: 90vw;'
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['class'] = 'grow'
        self.fields['password2'].widget.attrs['style'] = 'max-width: 90vw;'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'