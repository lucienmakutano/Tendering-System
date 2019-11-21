from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from tenderingSystem.model import Users
from wtforms import StringField, TextField, PasswordField, SelectField, SubmitField, BooleanField, IntegerField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Email, length, EqualTo, ValidationError


def validate_email(email):
    user = Users.query.filter_by(email=email.data).first()

    if user:
        raise ValidationError("this email address is taken please choose another one")


class RegisterForm(FlaskForm):
    email = TextField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), length(min=8, max=255)])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo('password'), length(min=8, max=255)])
    user_type = SelectField("Register as", choices=[('supplier', 'supplier'), ('buyer', 'buyer')],
                            validators=[DataRequired()])
    register = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), length(min=8, max=30)])
    remember = BooleanField("Remember Me")
    login = SubmitField('Login')


class NewsLetter(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Subscribe")


class TenderForm(FlaskForm):
    entity_name = StringField("Entity name", validators=[DataRequired()])
    entity_type = StringField("Entity type", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    status = StringField("Status", validators=[DataRequired(), length(min=4, max=8)])
    date_published = DateTimeLocalField("Date published", format='%Y-%m-%dT%H:%M')
    date_closed = DateTimeLocalField("Closing date", format='%Y-%m-%dT%H:%M')
    tender_document = FileField("Tender document",
                                validators=[FileAllowed(['pdf']), FileRequired()])
    submit = SubmitField("Publish")


class CompanyForm(FlaskForm):
    company_name = StringField("Company name", validators=[DataRequired()])
    phone_number = IntegerField("Telephone number", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    company_type = StringField("Company type", validators=[DataRequired()])
    submit = SubmitField("register")


class UpdateCompanyForm(FlaskForm):
    company_name = StringField("Company name", validators=[DataRequired()])
    phone_number = IntegerField("Telephone number", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    company_type = StringField("Company type", validators=[DataRequired()])
    submit = SubmitField("Update")


class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), length(min=8, max=30)])
    submit = SubmitField('Update')


class UploadBidForm(FlaskForm):
    bid_document = FileField("Upload Bid", validators=[FileRequired(), FileAllowed(['pdf'])])
    submit = SubmitField("Upload")


class UpdateTenderForm(FlaskForm):
    entity_name = StringField("Entity name", validators=[DataRequired()])
    entity_type = StringField("Entity type", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    status = StringField("Status", validators=[DataRequired(), length(min=4, max=8)])
    date_published = DateTimeLocalField("Date published", format='%Y-%m-%dT%H:%M')
    date_closed = DateTimeLocalField("Closing date", format='%Y-%m-%dT%H:%M')
    tender_document = FileField("Tender document",
                                validators=[FileAllowed(['pdf', 'ppt', 'pptx', 'docx']), FileRequired()])
    submit = SubmitField("Save changes")
