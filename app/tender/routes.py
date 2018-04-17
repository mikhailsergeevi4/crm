from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from app import db
from app.tender import bp
from app.tender.forms import NewTender, EditTender
from app.models import Tender
from werkzeug import secure_filename
from datetime import datetime, timedelta

@bp.route('/tenders/', methods=['GET', 'POST'])
@login_required
def showTenders():
    date = datetime.today() + timedelta(2)
    form = NewTender()
    if form.validate_on_submit():
        newTender = Tender(number=form.number.data, end_date=form.end_date.data, game_date=form.game_date.data, ground=form.ground.data, company=form.company.data, notes=form.notes.data, contract=form.contract.data, author=current_user)
        db.session.add(newTender)
        db.session.commit()
        flash('Новый тендер "{}" добавлен!'.format(form.number.data))
        return redirect(url_for('tender.showTenders'))
    tenders = Tender.query.order_by(Tender.end_date.asc())
    return render_template("/tender/tenders.html", title='Тендеры', tenders=tenders, form=form, date=date)


@bp.route('/tenders/<int:tender_id>/edit/', methods=['GET', 'POST'])
@login_required
def editTender(tender_id):
    tender = Tender.query.filter_by(id=tender_id).one()
    form = EditTender(tender.number, obj=tender)
    if form.validate_on_submit():
        tender.number = form.number.data
        tender.notes = form.notes.data
        tender.end_date = form.end_date.data
        tender.game_date = form.game_date.data
        tender.ground = form.ground.data
        tender.company = form.company.data
        tender.contract = form.contract.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('tender.showTenders'))
    return render_template('/tender/editTender.html', title='Редактирование тендера',
                           form=form, tender_id=tender_id)


@bp.route('/tenders/<int:tender_id>/del/', methods=['GET', 'POST'])
@login_required
def deleteTender(tender_id):
    tenderToDelete = Tender.query.filter_by(id=tender_id).one()
    db.session.delete(tenderToDelete)
    db.session.commit()
    flash('Тендер успешно удален')
    return redirect(url_for('tender.showTenders'))
