from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from app import db, images
from app.clients import bp
from app.clients.forms import NewRegion, NewClinic, EditClinic, NewPerson, EditPerson, NewVisit
from app.models import Clinic, Region, Person, Visit
from werkzeug import secure_filename



@bp.route('/regions/', methods=['GET', 'POST'])
@login_required
def showRegions():
    form = NewRegion()
    if form.validate_on_submit():
        newRegion = Region(name=form.region.data)
        db.session.add(newRegion)
        db.session.commit()
        flash('Новый регион "{}" добавлен!'.format(form.region.data))
        return redirect(url_for('clients.showRegions'))
    regions = Region.query.order_by(Region.name.asc())
    return render_template('/clients/regions.html', title='Regions', form=form, regions=regions)


# Show all clinics in region
@bp.route('/regions/<region_name>/clinics/', methods=['GET', 'POST'])
@login_required
def showClinics(region_name):
    form = NewClinic()
    if form.validate_on_submit():
        newClinic = Clinic(clinic_name=form.clinic_name.data, address=form.address.data, inn=form.inn.data, author=current_user, region_name=region_name)
        db.session.add(newClinic)
        db.session.commit()
        flash('Новая клиника "{}" добавлена!'.format(form.clinic_name.data))
        return redirect(url_for('clients.showClinics', region_name=region_name))
    region = Region.query.filter_by(name=region_name).one()
    page = request.args.get('page', 1, type=int)
    clinics = Clinic.query.filter_by(region_name=region_name).paginate(page, current_app.config['CLINICS_PER_PAGE'], False)
    next_url = url_for('clients.showClinics', page=clinics.next_num) \
        if clinics.has_next else None
    prev_url = url_for('clients.showClinics', page=clinics.prev_num) \
        if clinics.has_prev else None
    return render_template("/clients/clinics.html", title='Клиники', clinics=clinics.items,
                          next_url=next_url, prev_url=prev_url, region=region, form=form, region_name=region_name)


@bp.route('/regions/<region_name>/clinics/<int:clinic_id>/del/', methods=['GET', 'POST'])
@login_required
def deleteClinic(clinic_id, region_name):
    clinicToDelete = Clinic.query.filter_by(id=clinic_id).one()
    db.session.delete(clinicToDelete)
    db.session.commit()
    flash('Клиника успешно удалена')
    return redirect(url_for('clients.showClinics', region_name=region_name))


@bp.route('/regions/<region_name>/clinics/<int:clinic_id>/edit', methods=['GET', 'POST'])
@login_required
def editClinic(clinic_id, region_name):
    clinic = Clinic.query.filter_by(id=clinic_id).one()
    form = EditClinic(clinic.clinic_name, clinic.inn, obj=clinic)
    if form.validate_on_submit():
        clinic.clinic_name = form.clinic_name.data
        clinic.inn = form.inn.data
        clinic.address = form.address.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('clients.showClinics', region_name=region_name))
    region = Region.query.filter_by(name=region_name).one()

    return render_template('/clients/edit_clinic.html', title='Edit Clinic',
                           form=form, clinic_id=clinic_id, region_name=region_name)


@bp.route('/regions/<region_name>/clinics/<int:clinic_id>/persons/', methods=['GET', 'POST'])
@login_required
def showPersons(region_name, clinic_id):
    form = NewPerson()
    if form.validate_on_submit():
        if not form.picture_url.data:
             filename = '-.png'
             url = 'images/-.png'
        else:
            filename = images.save(request.files['picture_url'])
            url = images.url(filename)
        newPerson = Person(name=form.name.data, comments=form.comments.data, picture_filename=filename, picture_url=url, phone=form.phone.data, email=form.email.data, department=form.department.data, date_of_request=form.date_of_request.data, date_of_request2=form.date_of_request2.data, author=current_user, region_name=region_name, clinic_id=clinic_id)
        db.session.add(newPerson)
        db.session.commit()
        flash('Новый клиент "{}" добавлен!'.format(form.name.data))
        return redirect(url_for('clients.showPersons', clinic_id=clinic_id, region_name=region_name))
    persons = Person.query.filter_by(clinic_id=clinic_id).order_by(Person.last_visit.desc())
    clinic = Clinic.query.filter_by(id=clinic_id).one()
    return render_template("/clients/persons.html", title='Клиенты', persons=persons, form=form, region_name=region_name, clinic=clinic)


@bp.route('/regions/<region_name>/clinics/<int:clinic_id>/persons/<int:person_id>/edit/', methods=['GET', 'POST'])
@login_required
def editPerson(clinic_id, region_name, person_id):
    person = Person.query.filter_by(id=person_id).one()
    form = EditPerson(person.name, person.email, obj=person)
    if form.validate_on_submit():
        if form.picture_url.data == person.picture_url:
             url = form.picture_url.data
             filename = person.picture_filename
        else:
            filename = images.save(request.files['picture_url'])
            url = images.url(filename)
        person.name = form.name.data
        person.comments = form.comments.data
        person.picture_filename = filename
        person.picture_url = url
        person.phone = form.phone.data
        person.email = form.email.data
        person.department = form.department.data
        person.date_of_request = form.date_of_request.data
        person.date_of_request2 = form.date_of_request2.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('clients.showPersons', region_name=region_name, clinic_id=clinic_id))
    return render_template('/clients/edit_person.html', title='Edit Client',
                           form=form, person_id=person_id, clinic_id=clinic_id, region_name=region_name)


@bp.route('/regions/<region_name>/clinics/<int:clinic_id>/persons/<int:person_id>/del/', methods=['GET', 'POST'])
@login_required
def deletePerson(clinic_id, region_name, person_id):
    personToDelete = Person.query.filter_by(id=person_id).one()
    db.session.delete(personToDelete)
    db.session.commit()
    flash('Клиент успешно удален')
    return redirect(url_for('clients.showPersons', region_name=region_name, clinic_id=clinic_id))


@bp.route('/regions/<region_name>/clinics/<int:clinic_id>/persons/<int:person_id>/visits/', methods=['GET', 'POST'])
@login_required
def showVisits(region_name, clinic_id, person_id):
    form = NewVisit()
    person = Person.query.filter_by(id=person_id).one()
    if form.validate_on_submit():
        newVisit = Visit(date=form.date.data, date_of_next_visit=form.date_of_next_visit.data, arrangements=form.arrangements.data, author=current_user, person_id=person_id)
        db.session.add(newVisit)
        person.last_visit=Visit.query.filter_by(person_id=person_id).order_by(Visit.date.desc()).first().date
        person.next_visit=Visit.query.filter_by(person_id=person_id).order_by(Visit.date_of_next_visit.desc()).first().date_of_next_visit
        db.session.commit()
        flash('Новый визит к клиенту "{}" добавлен!'.format(person.name))
        return redirect(url_for('clients.showVisits', clinic_id=clinic_id, region_name=region_name, person_id=person_id))

    visits = Visit.query.filter_by(person_id=person_id).order_by(Visit.date.desc())
    return render_template("/clients/visits.html", title='Визиты', person=person, form=form, visits=visits, clinic_id=clinic_id, region_name=region_name)


@bp.route('/regions/<region_name>/clinics/<int:clinic_id>/persons/<int:person_id>/visits/del/<int:visit_id>', methods=['GET', 'POST'])
@login_required
def deleteVisit(region_name, clinic_id, person_id, visit_id):
    person = Person.query.filter_by(id=person_id).one()
    visitToDelete = Visit.query.filter_by(id=visit_id).one()
    db.session.delete(visitToDelete)
    lastVisit = Visit.query.filter_by(person_id=person_id).order_by(Visit.date.desc()).first()
    if not lastVisit:
        person.last_visit=None
        person.next_visit=None
    else:
        person.last_visit = lastVisit.date
        person.next_visit = lastVisit.date_of_next_visit
    db.session.commit()
    flash('Визит успешно удален')
    return redirect(url_for('clients.showVisits', person_id=person_id, clinic_id=clinic_id, region_name=region_name))
