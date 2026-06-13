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
        fields = ['first_name', 'last_name', 'bio', 'avatar', 'preferred_language']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself / اكتب نبذة عن yourself...'}),
        }
