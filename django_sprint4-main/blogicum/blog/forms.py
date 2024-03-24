from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Post, Comment, User


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': DateTimeLocalInput(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )


class RegistrationForm(UserCreationForm, forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )
