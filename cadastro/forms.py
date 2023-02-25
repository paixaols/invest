from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(RegisterUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.username = user.email
        if commit:
            user.save()
        return user
