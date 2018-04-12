from datetime import datetime
from flask import render_template, flash, redirect, request,\
    url_for, send_from_directory, jsonify, current_app
from app import db, images
from app.main.forms import  EditProfileForm, PostForm, NewRegion, NewClinic, EditClinic, NewPerson, EditPerson, NewVisit
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Post, Clinic, Region, User, Person, Visit #, Product, RU
from werkzeug.urls import url_parse
from app.main import bp
from werkzeug import secure_filename
import os




@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url, prev_url=prev_url)




@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved!.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url)


@bp.route('/regions/', methods=['GET', 'POST'])
@login_required
def showRegions():
    form = NewRegion()
    if form.validate_on_submit():
        newRegion = Region(name=form.region.data)
        db.session.add(newRegion)
        db.session.commit()
        flash('Новый регион "{}" добавлен!'.format(form.region.data))
        return redirect(url_for('main.showRegions'))
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
        return redirect(url_for('main.showClinics', region_name=region_name))
    region = Region.query.filter_by(name=region_name).one()
    page = request.args.get('page', 1, type=int)
    clinics = Clinic.query.filter_by(region_name=region_name).paginate(page, current_app.config['CLINICS_PER_PAGE'], False)
    next_url = url_for('main.showClinics', page=clinics.next_num) \
        if clinics.has_next else None
    prev_url = url_for('main.showClinics', page=clinics.prev_num) \
        if clinics.has_prev else None
    return render_template("/clients/clinics.html", title='Клиники', clinics=clinics.items,
                          next_url=next_url, prev_url=prev_url, region=region, form=form, region_name=region_name)



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
        return redirect(url_for('main.showClinics', region_name=region_name))
    region = Region.query.filter_by(name=region_name).one()

    return render_template('/clients/edit_clinic.html', title='Edit Clinic',
                           form=form, clinic_id=clinic_id, region_name=region_name)


@bp.route('/regions/<region_name>/clinics/<int:clinic_id>/persons/', methods=['GET', 'POST'])
@login_required
def showPersons(region_name, clinic_id):
    form = NewPerson()
    if form.validate_on_submit():
        filename = images.save(request.files['picture_url'])
        url = images.url(filename)
        newPerson = Person(name=form.name.data, comments=form.comments.data, picture_filename=filename, picture_url=url, phone=form.phone.data, email=form.email.data, department=form.department.data, date_of_request=form.date_of_request.data, author=current_user, clinic_id=clinic_id)
        db.session.add(newPerson)
        db.session.commit()
        flash('Новый клиент "{}" добавлен!'.format(form.name.data))
        return redirect(url_for('main.showPersons', clinic_id=clinic_id, region_name=region_name))
    persons = Person.query.filter_by(clinic_id=clinic_id).order_by(Person.last_visit.desc())
    clinic = Clinic.query.filter_by(id=clinic_id).one()
    return render_template("/clients/persons.html", title='Клиенты', persons=persons, form=form, region_name=region_name, clinic=clinic)


@bp.route('/regions/<region_name>/clinics/<int:clinic_id>/persons/<int:person_id>/edit/', methods=['GET', 'POST'])
@login_required
def editPerson(clinic_id, region_name, person_id):
    person = Person.query.filter_by(id=person_id).one()
    #person.date_of_request = datetime.strptime(person.date_of_request, '%Y-%m-%d %H:%M:%S')
    form = EditPerson(person.name, person.email, obj=person)
    if form.validate_on_submit():
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
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('main.showPersons', region_name=region_name, clinic_id=clinic_id))
    region = Region.query.filter_by(name=region_name).one()

    return render_template('/clients/edit_person.html', title='Edit Client',
                           form=form, person_id=person_id, clinic_id=clinic_id, region_name=region_name)


@bp.route('/regions/<region_name>/clinics/<int:clinic_id>/persons/<int:person_id>/del/', methods=['GET', 'POST'])
@login_required
def deletePerson(clinic_id, region_name, person_id):
    personToDelete = Person.query.filter_by(id=person_id).one()
    db.session.delete(personToDelete)
    db.session.commit()
    flash('Клиент успешно удален')
    return redirect(url_for('main.showPersons', region_name=region_name, clinic_id=clinic_id))


@bp.route('/regions/<region_name>/clinics/<int:clinic_id>/persons/<int:person_id>/visits/', methods=['GET', 'POST'])
@login_required
def showVisits(region_name, clinic_id, person_id):
    form = NewVisit()
    person = Person.query.filter_by(id=person_id).one()
    if form.validate_on_submit():
        newVisit = Visit(date=form.date.data, date_of_next_visit=form.date_of_next_visit.data, arrangements=form.arrangements.data, author=current_user, person_id=person_id)
        person.last_visit=form.date.data
        person.next_visit=form.date_of_next_visit.data
        db.session.add(newVisit)
        db.session.commit()
        flash('Новый визит к клиенту "{}" добавлен!'.format(person.name))
        return redirect(url_for('main.showVisits', clinic_id=clinic_id, region_name=region_name, person_id=person_id))

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
        person.last_visit='None'
        person.next_visit='None'
    else:
        person.last_visit=lastVisit.date
        person.next_visit=lastVisit.date_of_next_visit
    db.session.commit()
    flash('Визит успешно удален')
    return redirect(url_for('main.showVisits', person_id=person_id, clinic_id=clinic_id, region_name=region_name))
