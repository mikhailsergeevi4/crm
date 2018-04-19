from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from app import db
from app.contract import bp
from app.contract.forms import NewContract, EditContract
from app.models import Contract
from werkzeug import secure_filename
from datetime import datetime, timedelta


@bp.route('/contracts/', methods=['GET', 'POST'])
@login_required
def showContracts():
    date = datetime.today() + timedelta(2)
    form = NewContract()
    if form.validate_on_submit():
        newContract = Contract(number=form.number.data, sign_date=form.sign_date.data, ground=form.ground.data, company=form.company.data, notes=form.notes.data, customer=form.customer.data, supply=form.supply.data, author=current_user)
        db.session.add(newContract)
        db.session.commit()
        flash('Новый контракт в "{}" добавлен!'.format(form.customer.data))
        return redirect(url_for('contract.showContracts'))
    contracts = Contract.query.order_by(Contract.sign_date.asc())
    return render_template("/contract/contracts.html", title='Контракты', contracts=contracts, form=form, date=date)


@bp.route('/contracts/<int:contract_id>/edit/', methods=['GET', 'POST'])
@login_required
def editContract(contract_id):
    contract = Contract.query.filter_by(id=contract_id).one()
    form = EditContract(obj=contract)
    if form.validate_on_submit():
        contract.notes = form.notes.data
        contract.sign_date = form.sign_date.data
        contract.supply = form.supply.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('contract.showContracts'))
    return render_template('/contract/editContract.html', title='Редактирование контракта',
                           form=form, contract_id=contract_id)


@bp.route('/contracts/<int:contract_id>/del/', methods=['GET', 'POST'])
@login_required
def deleteContract(contract_id):
    contractToDelete = Contract.query.filter_by(id=contract_id).one()
    db.session.delete(contractToDelete)
    db.session.commit()
    flash('Контракт успешно удален')
    return redirect(url_for('contract.showContracts'))
