from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, SelectField, TextAreaField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import Contract, Clinic
from wtforms.fields.html5 import DateField


choices_ground = [('Сбербанк-АСТ','Сбербанк-АСТ'), ('РТС-Тендер', 'РТС-Тендер'), ('ЕЭТП', 'ЕЭТП'), ('OTC', 'OTC'), ('Другая', 'Другая')]
choices_company = [('ШАГ-Урал','ШАГ-Урал'), ('УМТК', 'УМТК')]
#clinics = Clinic.query.all()
#choices_clinic = clinics.clinic_name


class NewContract(FlaskForm):
    number = StringField('Номер аукциона', validators=[DataRequired()])
    sign_date = DateField('Дата окончания срока подписания')
    ground = SelectField('Площадка', choices=choices_ground)
    company = SelectField('Компания', choices=choices_company)
    notes = TextAreaField('Примечания')
    customer = SelectField('Заказчик', choices=choices_company)
    supply = StringField('Размер обеспечения')
    submit = SubmitField('Добавить')

    def validate_number(self, number):
        contract = Contract.query.filter_by(number=number.data).first()
        if contract is not None:
            raise ValidationError('Аукцион с данным номером уже есть в базе')


class EditContract(FlaskForm):
    sign_date = DateField('Дата окончания срока подписания')
    notes = TextAreaField('Примечания')
    supply = StringField('Размер обеспечения')
    submit = SubmitField('Сохранить изменения')
