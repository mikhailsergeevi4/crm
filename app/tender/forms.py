from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, SelectField, TextAreaField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Length, Regexp
from app.models import Tender, Clinic
from wtforms.fields.html5 import DateField

choices_ground = [('Сбербанк-АСТ','Сбербанк-АСТ'), ('РТС-Тендер', 'РТС-Тендер'), ('ЕЭТП', 'ЕЭТП'), ('OTC', 'OTC'), ('Другая', 'Другая')]
choices_company = [('ШАГ-Урал','ШАГ-Урал'), ('УМТК', 'УМТК')]



class NewTender(FlaskForm):
    number = StringField('Номер аукциона', validators=[DataRequired()])
    end_date = DateField('Дата окончания подачи заявок')
    game_date = DateField('Дата проведения ауцкиона')
    ground = SelectField('Площадка', choices=choices_ground)
    company = SelectField('Компания', choices=choices_company)
    notes = TextAreaField('Примечания')
    customer = SelectField('Заказчик')
    submit = SubmitField('Добавить')

    def validate_number(self, number):
        tender = Tender.query.filter_by(number=number.data).first()
        if tender is not None:
            raise ValidationError('Аукцион с данным номером уже есть в базе')

    def __init__(self):
        super(NewTender, self).__init__()
        clinics = Clinic.query.all()
        choices = [(g.clinic_name, g.clinic_name) for g in Clinic.query.all()]
        self.customer.choices = choices

class EditTender(FlaskForm):
    number = StringField('Номер аукциона', validators=[DataRequired()])
    end_date = DateField('Дата окончания подачи заявок')
    game_date = DateField('Дата проведения ауцкиона')
    ground = SelectField('Площадка', choices=choices_ground)
    company = SelectField('Компания', choices=choices_company)
    notes = TextAreaField('Примечания')
    customer = SelectField('Заказчик')
    submit = SubmitField('Сохранить изменения')

    def __init__(self, original_number, *args, **kwargs):
        super(EditTender, self).__init__(*args, **kwargs)
        clinics = Clinic.query.all()
        choices = [(g.clinic_name, g.clinic_name) for g in Clinic.query.all()]
        self.customer.choices = choices
        self.original_number = original_number


    def validate_number(self, number):
        if number.data != self.original_number:
            tender = Tender.query.filter_by(number=number.data).first()
            if tender is not None:
                raise ValidationError('Аукцион с данным номером уже есть в базе')
