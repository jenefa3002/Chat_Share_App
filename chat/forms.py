from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


from django import forms
from .models import Message

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'file']  # Include file field

