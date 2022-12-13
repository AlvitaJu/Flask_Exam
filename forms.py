from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, BooleanField, FloatField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
import main
from flask_wtf.file import FileField, FileAllowed


def get_pk(obj):
    return str(obj)


def bill_query():
    return main.Bill.query


def group_query():
    return main.Group.query


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password1 = PasswordField('Password 1', validators=[DataRequired()])
    password2 = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password1')])

    def validate_email(self, email):
        user = main.User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('User email is bad :(')


class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class BillsForm(FlaskForm):
    amount = StringField('Amount', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Add')


class GroupsForm(FlaskForm):
    group_id = StringField('Group_id', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    bills = QuerySelectMultipleField(query_factory=main.Bill.query.all, get_label="description",
                                     get_pk=lambda obj: str(obj))
    submit = SubmitField('Add')



