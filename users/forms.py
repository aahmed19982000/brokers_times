from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name / الاسم الأول")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name / اسم العائلة")
    email = forms.EmailField(required=True, label="Email / البريد الإلكتروني")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'preferred_language')

class CustomUserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'bio', 'avatar', 'preferred_language', 'facebook_url', 'linkedin_url']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself / اكتب نبذة عن yourself...'}),
            'facebook_url': forms.URLInput(attrs={'placeholder': 'e.g. https://facebook.com/username'}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'e.g. https://linkedin.com/in/username'}),
        }


class DashboardUserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password...', 'class': 'form-input-editor'}), required=True, label="Password / كلمة المرور")
    can_publish = forms.BooleanField(required=False, label="Can Publish / صلاحية النشر")
    can_edit = forms.BooleanField(required=False, label="Can Edit / صلاحية التعديل")
    can_manage_brokers = forms.BooleanField(required=False, label="Manage Brokers / إدارة الوسطاء")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input-editor', 'placeholder': 'Username...'}),
            'email': forms.EmailInput(attrs={'class': 'form-input-editor', 'placeholder': 'Email...'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input-editor', 'placeholder': 'First Name...'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input-editor', 'placeholder': 'Last Name...'}),
            'role': forms.Select(attrs={'class': 'form-input-editor'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            from django.contrib.auth.models import Permission
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get_for_model(CustomUser)
            
            perms = []
            if self.cleaned_data.get('can_publish'):
                perms.append(Permission.objects.get(codename='can_publish', content_type=content_type))
            if self.cleaned_data.get('can_edit'):
                perms.append(Permission.objects.get(codename='can_edit', content_type=content_type))
            if self.cleaned_data.get('can_manage_brokers'):
                perms.append(Permission.objects.get(codename='can_manage_brokers', content_type=content_type))
            
            user.user_permissions.set(perms)
            
            if user.role == 'admin':
                user.is_staff = True
            else:
                user.is_staff = False
            user.save()
        return user


class DashboardUserUpdateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Leave blank to keep current password...', 'class': 'form-input-editor'}), required=False, label="Password / كلمة المرور")
    can_publish = forms.BooleanField(required=False, label="Can Publish / صلاحية النشر")
    can_edit = forms.BooleanField(required=False, label="Can Edit / صلاحية التعديل")
    can_manage_brokers = forms.BooleanField(required=False, label="Manage Brokers / إدارة الوسطاء")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input-editor', 'placeholder': 'Username...'}),
            'email': forms.EmailInput(attrs={'class': 'form-input-editor', 'placeholder': 'Email...'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input-editor', 'placeholder': 'First Name...'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input-editor', 'placeholder': 'Last Name...'}),
            'role': forms.Select(attrs={'class': 'form-input-editor'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['can_publish'].initial = self.instance.user_permissions.filter(codename='can_publish').exists()
            self.fields['can_edit'].initial = self.instance.user_permissions.filter(codename='can_edit').exists()
            self.fields['can_manage_brokers'].initial = self.instance.user_permissions.filter(codename='can_manage_brokers').exists()

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
            from django.contrib.auth.models import Permission
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get_for_model(CustomUser)
            
            perms = []
            if self.cleaned_data.get('can_publish'):
                perms.append(Permission.objects.get(codename='can_publish', content_type=content_type))
            if self.cleaned_data.get('can_edit'):
                perms.append(Permission.objects.get(codename='can_edit', content_type=content_type))
            if self.cleaned_data.get('can_manage_brokers'):
                perms.append(Permission.objects.get(codename='can_manage_brokers', content_type=content_type))
            
            user.user_permissions.set(perms)
            
            if user.role == 'admin':
                user.is_staff = True
            else:
                user.is_staff = False
            user.save()
        return user
