from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, DateTimeField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Regexp
from app.models import User, Clinic, Person
import re

from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import images


choices = [('Урологическое','Урологическое'), ('Эндоскопическое', 'Эндоскопическое')]


class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Сохранить')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Выберите другое имя пользователя')


class PostForm(FlaskForm):
    post = TextAreaField('Скажите что-нибудь', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Отправить')


class NewRegion(FlaskForm):
    region = StringField('Введите название региона', validators=[
        DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Добавить')


class NewClinic(FlaskForm):
    clinic_name = StringField('Введите название клиники', validators=[
        DataRequired(), Length(min=1, max=180)])
    address = StringField('Введите адрес клиники', validators=[
        DataRequired(), Length(min=1, max=250)])
    inn = StringField('Введите ИНН клиники', validators=[
        DataRequired(), Length(min=10, max=10, message='Вы ввели неккоректный ИНН')])
    submit = SubmitField('Добавить')

    def validate_clinic_name(self, clinic_name):
        clinic = Clinic.query.filter_by(clinic_name=clinic_name.data).first()
        if clinic is not None:
            raise ValidationError('Клиника с указанным наименованием уже присутствует в базе')

    def validate_inn(self, inn):
        inn = Clinic.query.filter_by(inn=inn.data).first()
        if inn is not None:
            raise ValidationError('Клиника с указанным ИНН уже присутствует в базе')


class EditClinic(FlaskForm):
    clinic_name = StringField('Введите название клиники', validators=[
        DataRequired(), Length(min=1, max=180)])
    address = StringField('Введите адрес клиники', validators=[
        DataRequired(), Length(min=1, max=250)])
    inn = StringField('Введите ИНН клиники', validators=[
        DataRequired(), Length(min=10, max=10, message='Вы ввели неккоректный ИНН')])
    submit = SubmitField('Сохранить')

    def __init__(self, original_clinic_name, original_clinic_inn, *args, **kwargs):
        super(EditClinic, self).__init__(*args, **kwargs)
        self.original_clinic_name = original_clinic_name
        self.original_clinic_inn = original_clinic_inn

    def validate_clinic_name(self, clinic_name):
        if clinic_name.data != self.original_clinic_name:
            clinic = Clinic.query.filter_by(clinic_name=clinic_name.data).first()
            if clinic is not None:
                raise ValidationError('Клиника с указанным наименованием уже присутствует в базе')

    def validate_inn(self, inn):
        if inn.data != self.original_clinic_inn:
            inn = Clinic.query.filter_by(inn=inn.data).first()
            if inn is not None:
                raise ValidationError('Клиника с указанным ИНН уже присутствует в базе')


class NewPerson(FlaskForm):
    name = StringField('ФИО', validators=[
        DataRequired(), Length(min=1, max=180)])
    comments = TextAreaField('Примечания', validators=[Length(min=1, max=250)])
    picture_url = FileField('Фотография', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    phone = StringField('Введите телефон', validators=[Length(min=1, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = SelectField('Отделение', choices=choices)
    date_of_request = DateTimeField('Дата подготовки заявки на закуп', format='%d-%m-%Y')
    submit = SubmitField('Добавить', id="submit_id")

    def validate_email(self, email):
        person = Person.query.filter_by(email=email.data).first()
        if person is not None:
            raise ValidationError('Данный e-mail принадлежит другому клиенту')

    def validate_phone(self, phone):
        phone = Person.query.filter_by(phone=phone.data).first()
        if phone is not None:
            raise ValidationError('Данный телефон принадлежит другому клиенту')


class EditPerson(FlaskForm):
    name = StringField('ФИО', validators=[
        DataRequired(), Length(min=1, max=180)])
    comments = TextAreaField('Примечания', validators=[Length(min=1, max=250)])
    picture_url = FileField('Фотография', validators=[FileRequired(), FileAllowed(images, 'Images only!')])
    phone = StringField('Введите телефон', validators=[Length(min=1, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = SelectField('Отделение', choices=choices)
    date_of_request = DateTimeField('Дата подготовки заявки на закуп', format='%d-%m-%Y')
    submit = SubmitField('Сохранить изменения', id="submit_id")

    def __init__(self, original_person_name, original_person_email, *args, **kwargs):
        super(EditPerson, self).__init__(*args, **kwargs)
        self.original_person_name = original_person_name
        self.original_person_email = original_person_email

    def validate_name(self, name):
        if name.data != self.original_person_name:
            person = Person.query.filter_by(name=name.data).first()
            if person is not None:
                raise ValidationError('Клиент с указанным ФИО уже присутствует в базе')

    def validate_email(self, email):
        if email.data != self.original_person_email:
            email = Person.query.filter_by(email=email.data).first()
            if email is not None:
                raise ValidationError('Клиент с указанной почтой уже присутствует в базе')


class NewVisit(FlaskForm):
    date = DateTimeField('Дата',validators=[DataRequired()], format='%d-%m-%Y')
    date_of_next_visit = DateTimeField('Дата следующего визита',validators=[DataRequired()], format='%d-%m-%Y')
    arrangements = TextAreaField('Примечания', validators=[Length(min=1, max=250)])
    submit = SubmitField('Добавить', id="submit_id")
