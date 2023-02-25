from django.test import TestCase

from .forms import RegisterUserForm
from .models import User


#--------------------------------------------------#
# Test models
#--------------------------------------------------#
class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email='test@dev.com', password='123')
        self.assertEqual(user.username, 'test@dev.com')
        self.assertEqual(user.email, 'test@dev.com')
        self.assertIs(user.is_active, True)
        self.assertIs(user.is_staff, False)
        self.assertIs(user.is_superuser, False)

    def test_create_superuser(self):
        user = User.objects.create_superuser(email='test@dev.com', password='123')
        self.assertEqual(user.username, 'test@dev.com')
        self.assertEqual(user.email, 'test@dev.com')
        self.assertIs(user.is_active, True)
        self.assertIs(user.is_staff, True)
        self.assertIs(user.is_superuser, True)


#--------------------------------------------------#
# Test forms
#--------------------------------------------------#
class RegisterUserFormTest(TestCase):
    def test_register_user_with_invalid_email(self):
        form_data = {
            'email': 'test',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'StrongP4ss!',
            'password2': 'StrongP4ss!'
        }
        form = RegisterUserForm(data=form_data)
        self.assertIs(form.is_valid(), False)

    def test_register_user_with_invalid_password(self):
        form_data = {
            'email': 'test',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': '123',
            'password2': '123'
        }
        form = RegisterUserForm(data=form_data)
        self.assertIs(form.is_valid(), False)

    def test_register_user_with_different_passwords(self):
        form_data = {
            'email': 'test',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'StrongP4ss!',
            'password2': 'WrongP4ss!',
        }
        form = RegisterUserForm(data=form_data)
        self.assertIs(form.is_valid(), False)

    def test_register_user_with_valid_information(self):
        form_data = {
            'email': 'test@dev.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'StrongP4ss!',
            'password2': 'StrongP4ss!'
        }
        form = RegisterUserForm(data=form_data)
        self.assertIs(form.is_valid(), True)
        user = form.save()
        self.assertEqual(user.email, 'test@dev.com')
        self.assertEqual(user.username, 'test@dev.com')
