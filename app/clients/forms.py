from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, DateTimeField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length, Email, Regexp
from app.models import User, Clinic, Person
from wtforms.fields.html5 import DateField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app import images
import re

choices = [('Урологическое','Урологическое'),
            ('Эндоскопическое', 'Эндоскопическое'),
            ('Администрация', 'Администрация'),
            ('ВРТ', 'ВРТ'),
            ('Рентгенхирургическое', 'Рентгенхирургическое'),
            ('ОАР', 'ОАР'),
            ('Оперблок', 'Оперблок'),
            ('Закупки', 'Закупки'),
            ('ОРИТ', 'ОРИТ'),
            ('ЦСО', 'ЦСО'),
            ('Физиотерапевтическое', 'Физиотерапевтическое'),
            ('Нейрохирургия', 'Нейрохирургия'),
            ('Кардиохирургия', 'Кардиохирургия'),
            ('ОАР новорожденных', 'ОАР новорожденных'),
            ('РАО Нейрохирургии', 'РАО Нейрохирургии'),
            ('АРО', 'АРО'),
            ('Диализ/Гемодиализ', 'Диализ/Гемодиализ'),
            ('Гематология', 'Гематология')б
            ('Другое', 'Другое')]


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
    picture_url = FileField('Фотография', validators=[FileAllowed(images, 'Images only!')])
    phone = StringField('Введите телефон', validators=[Length(min=1, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = SelectField('Отделение', choices=choices)
    date_of_request = DateField('Дата подготовки заявки на закуп')
    date_of_request2 = DateField('Дата подготовки заявки на закуп')
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
    picture_url = FileField('Фотография', validators=[FileAllowed(images, 'Images only!')])
    phone = StringField('Введите телефон', validators=[Length(min=1, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = SelectField('Отделение', choices=choices)
    date_of_request = DateField('Дата подготовки заявки на закуп')
    date_of_request2 = DateField('Дата подготовки заявки на закуп')
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
    date = DateField('Дата')
    date_of_next_visit = DateField('Дата следующего визита')
    arrangements = TextAreaField('Примечания', validators=[Length(min=1, max=250)])
    submit = SubmitField('Добавить', id="submit_id")
