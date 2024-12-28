from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import length, email, data_required, equal_to, ValidationError
from market.module import User

class RegisterForm(FlaskForm):
    
    def validate_username(self, username_to_check):
        if User.query.filter_by(username=username_to_check.data).first():
            raise ValidationError("Username already exists! Please choose another one")
    
    def validate_email(self, email_to_check):
        if User.query.filter_by(email=email_to_check.data).first():
            raise ValidationError("Email already exists! Please try to login")
    
    username = StringField(label="Username", validators=[length(min=4,max=24),data_required()])
    email = StringField(label="Email Address", validators=[email(),data_required()])
    password1 = PasswordField(label="Password", validators=[length(min=8,max=16),data_required()])
    password2 = PasswordField(label="Password", validators=[equal_to('password1'),data_required()])
    submit = SubmitField(label="Create Account")
    
class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[length(min=4,max=24),data_required()])
    password = PasswordField(label="Password", validators=[data_required()])
    submit = SubmitField(label="Login")
    
class AddProduct(FlaskForm):
    submit = SubmitField(label="Add to Cart")

class PlaceYourOrder(FlaskForm):
    submit = SubmitField(label="Place your order") 
    