from flask_wtf import FlaskForm
from wtforms import (
    BooleanField, DateTimeField, SelectField, StringField, PasswordField
)
from wtforms.validators import InputRequired, ValidationError


class RegisterForm(FlaskForm):
    name = StringField('name', validators=[InputRequired()])
    email = StringField('email', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    confirm_password = PasswordField(
        'confirm_password', validators=[InputRequired()]
    )


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])


def datetime_validator(form, field):
    if not form.unexpirable.data and field.data is None:
        raise ValidationError('Datetime validation error')


class AssetForm(FlaskForm):
    name = StringField('name', validators=[InputRequired()])
    description = StringField('description', validators=[InputRequired()])
    market = StringField('market', validators=[InputRequired()])
    asset_type = StringField('asset_type', validators=[InputRequired()])
    asset_group = StringField('asset_group', validators=[InputRequired()])
    expiration_date = DateTimeField(
        'expiration_date', 
        format='%d/%m/%Y', 
        validators=[datetime_validator]
    )
    unexpirable = BooleanField('unexpirable')


class WalletEntryForm(FlaskForm):
    market = SelectField('market')
    asset_type = SelectField('asset_type')
    asset_group = SelectField('asset_group')
    asset = SelectField('asset')
    # quantity = DecimalField() FloatField()
    # institution
    # cost
    # value
