from flask import render_template, flash, redirect, request, url_for, send_from_directory, jsonify
from app import app, db, images
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, NewRegion, NewClinic, EditClinic, NewPerson
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Post, Clinic, Region, User, Person #Visit, Product, RU
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
from werkzeug import secure_filename
import os


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc !='':
            next_page = url_for('index')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign in', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved!.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)



@app.route('/regions/', methods=['GET', 'POST'])
@login_required
def showRegions():
    form = NewRegion()
    if form.validate_on_submit():
        newRegion = Region(name=form.region.data)
        db.session.add(newRegion)
        db.session.commit()
        flash('Новый регион "{}" добавлен!'.format(form.region.data))
        return redirect(url_for('showRegions'))
    regions = Region.query.order_by(Region.name.asc())
    return render_template('regions.html', title='Regions', form=form, regions=regions)



#@app.route('/regions/<int:region_id>/delete/', methods=['GET', 'POST'])
#@login_required
#def deleteRegion(region_id):
    #regionToDelete = session.query(Region).filter_by(id=region_id).one()
    #if request.method == 'POST':
        #session.delete(regionToDelete)
        #flash('%s успешно удален' % regionToDelete.name)
        #session.commit()
        #return redirect(url_for('showRegions', region_id=region_id))
    #else:
        #return render_template('dregion.html', region=regionToDelete)

# Show all clinics in region
@app.route('/regions/<region_name>/clinics/', methods=['GET', 'POST'])
@login_required
def showClinics(region_name):
    form = NewClinic()
    if form.validate_on_submit():
        newClinic = Clinic(clinic_name=form.clinic_name.data, address=form.address.data, inn=form.inn.data, author=current_user, region_name=region_name)
        db.session.add(newClinic)
        db.session.commit()
        flash('Новая клиника "{}" добавлена!'.format(form.clinic_name.data))
        return redirect(url_for('showClinics', region_name=region_name))
    region = Region.query.filter_by(name=region_name).one()
    page = request.args.get('page', 1, type=int)
    clinics = Clinic.query.filter_by(region_name=region_name).paginate(page, app.config['CLINICS_PER_PAGE'], False)
    next_url = url_for('showClinics', page=clinics.next_num) \
        if clinics.has_next else None
    prev_url = url_for('showClinics', page=clinics.prev_num) \
        if clinics.has_prev else None
    return render_template("clinics.html", title='Клиники', clinics=clinics.items,
                          next_url=next_url, prev_url=prev_url, region=region, form=form, region_name=region_name)



@app.route('/regions/<region_name>/clinics/<int:clinic_id>/edit', methods=['GET', 'POST'])
@login_required
def editClinic(clinic_id, region_name):
    clinic = Clinic.query.filter_by(id=clinic_id).one()
    form = EditClinic(clinic.clinic_name, clinic.inn)
    if form.validate_on_submit():
        clinic.clinic_name = form.clinic_name.data
        clinic.inn = form.inn.data
        clinic.address = form.address.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('showClinics', region_name=region_name))
    elif request.method == 'GET':
        form.clinic_name.data=clinic.clinic_name
        form.inn.data=clinic.inn
        form.address.data=clinic.address
    region = Region.query.filter_by(name=region_name).one()

    return render_template('edit_clinic.html', title='Edit Clinic',
                           form=form, clinic_id=clinic_id, region_name=region_name)


# Delete a Element
#@app.route('/regions/<int:region_id>/clinics/<int:clinic_id>/delete', methods=[
    #'GET', 'POST'])
#@login_required
#def deleteClinic(region_id, clinic_id):
    #region = session.query(Region).filter_by(id=region_id).one()
    #clinicToDelete = session.query(Clinic).filter_by(id=clinic_id).one()
    #if request.method == 'POST':
        #session.delete(clinicToDelete)
        #session.commit()
        #flash('Клиника успешно удалена')
        #return redirect(url_for('showClinics', region_id=region_id))
    #else:
        #return render_template(
            #'dclinic.html', clinic=clinicToDelete, region=region)


# Show all persons

@app.route('/regions/<region_name>/clinics/<int:clinic_id>/persons/', methods=['GET', 'POST'])
@login_required
def showPersons(region_name, clinic_id):
    form = NewPerson()
    if form.validate_on_submit():
        filename = images.save(request.files['picture'])
        url = images.url(filename)
        newPerson = Person(name=form.name.data, comments=form.comments.data, picture_filename=filename, picture_url=url, phone=form.phone.data, email=form.email.data, department=form.department.data, last_visit=form.last_visit.data, next_visit=form.next_visit.data, date_of_request=form.date_of_request.data, author=current_user, clinic_id=clinic_id)
        db.session.add(newPerson)
        db.session.commit()
        flash('Новый клиент "{}" добавлен!'.format(form.name.data))
        return redirect(url_for('showPersons', clinic_id=clinic_id, region_name=region_name))
    persons = Person.query.order_by(Person.last_visit.desc())
    clinic = Clinic.query.filter_by(id=clinic_id).one()
    return render_template("persons.html", title='Клиенты', persons=persons, form=form, region_name=region_name, clinic=clinic)


@app.route('/regions/<region_name>/clinics/<int:clinic_id>/persons/<int:person_id>/edit/', methods=['GET', 'POST'])
@login_required
def editPerson(clinic_id, region_name, person_id):
    person = Person.query.filter_by(id=person_id).one()
    form = EditPerson(person.email, person.phone, person.picture)
    if form.validate_on_submit():
        person.name = form.person.data
        person.comments = form.person.comments
        person.picture = form.picture.data
        person.phone = form.phone.data
        person.email = form.email.data
        person.department = form.department.data
        person.last_visit = form.last_visit.data
        person.next_visit = form.next_visit.data
        person.date_of_request = form.date_of_request.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('showPersons', region_name=region_name, clinic_id=clinic_id))
    elif request.method == 'GET':
        form.clinic_name.data=clinic.clinic_name
        form.inn.data=clinic.inn
        form.address.data=clinic.address
        form.person.name = person.data
        form.person.comments = person.comments
        form.person.picture = picture.data
        form.person.phone = phone.data
        form.person.email = email.data
        form.person.department = department.data
        form.person.last_visit = last_visit.data
        form.person.next_visit = next_visit.data
        form.person.date_of_request = date_of_request.data
    region = Region.query.filter_by(name=region_name).one()

    return render_template('edit_person.html', title='Edit Client',
                           form=form, clinic_id=clinic_id, region_name=region_name)

# Create a new Person
#@app.route('/regions/<int:region_id>/clinics/<int:clinic_id>/persons/new', methods=['GET', 'POST'])
#@login_required
#def newPerson(clinic_id, region_id):
    #clinic = session.query(Clinic).filter_by(id=clinic_id).one()
    #if request.method == 'POST':
        #file = request.files['file']
        #if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename)
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #newPerson = Person(
                #name=request.form['name'],
                #picture=filename, phone=request.form['phone'],
                #email=request.form['email'], last_visit=request.form['last_visit'],
                #next_visit=request.form['next_visit'], comments=request.form['comments'], department=request.form['department'], date_of_request=request.form['date_of_request'], clinic_id=clinic_id)
            #session.add(newPerson)
            #flash('Новый клиент %s Успешно добавлен' % newPerson.name)
            #session.commit()
            #return redirect(url_for('showPersons', clinic_id=clinic_id, region_id=region_id))
        #else:
            #return responseWith('Bad image.', 422)
    #else:
        #return render_template('nperson.html', clinic_id=clinic_id, region_id=region_id)


# Edit a Person
#@app.route('/regions/<int:region_id>/clinics/<int:clinic_id>/persons/<int:person_id>/edit/', methods=['GET', 'POST'])
#@login_required
#def editPerson(person_id, region_id, clinic_id):
    #editedPerson = session.query(Person).filter_by(id=person_id).one()
    #if request.method == 'POST':
        #if request.form['date_of_request']:
            #editedPerson.date_of_request = request.form['date_of_request']
        #if request.form['next_visit']:
            #editedPerson.next_visit = request.form['next_visit']
        #if request.form['last_visit']:
            #editedPerson.last_visit = request.form['last_visit']
        #if request.form['comments']:
            #editedPerson.comments = request.form['comments']
        #if request.form['department']:
            #editedPerson.department = request.form['department']
        #if request.form['email']:
            #editedPerson.email = request.form['email']
        #if request.form['phone']:
            #editedPerson.phone = request.form['phone']
        #if request.files['file']:
            #file = request.files['file']
            #if file and allowed_file(file.filename):
                #filename = secure_filename(file.filename)
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #editedPerson.picture = filename
            #else:
                #return responseWith('Bad Image', 422)
        #if request.form['name']:
            #editedPerson.name = request.form['name']
        #flash('Клиент %s успешно отредактирован' % editedPerson.name)
        #return redirect(url_for('showPersons', person_id=person_id, region_id=region_id, clinic_id= clinic_id))
    #else:
        #return render_template('eperson.html', person=editedPerson, region_id=region_id, clinic_id= clinic_id)


# Delete a Cake
#@app.route('/regions/<int:region_id>/clinics/<int:clinic_id>/persons/<int:person_id>/delete/', methods=['GET', 'POST'])
#@login_required
#def deletePerson(person_id, region_id, clinic_id):
    #personToDelete = session.query(Person).filter_by(id=person_id).one()
    #if request.method == 'POST':
        #session.delete(personToDelete)
        #flash('%s успешно удален' % personToDelete.name)
        #session.commit()
        #return redirect(url_for('showPersons', person_id=person_id, region_id=region_id, clinic_id= clinic_id))
    #else:
        #return render_template('dperson.html', person=personToDelete, region_id=region_id, clinic_id= clinic_id)


# Show elements in person
#@app.route('/regions/<int:region_id>/clinics/<int:clinic_id>/persons/<int:person_id>/visits/')
#@login_required
#def showVisits(person_id, region_id, clinic_id):
    #person = session.query(Person).filter_by(id=person_id).one()
    #visits = session.query(Visit).filter_by(person_id=person_id).all()
    #return render_template('visits.html', visits=visits, person=person, clinic_id=clinic_id, region_id=region_id)


# Create a new Element
#@app.route('/regions/<int:region_id>/clinics/<int:clinic_id>/persons/<int:person_id>/visits/new/', methods=['GET', 'POST'])
#@login_required
#def newVisit(person_id, region_id, clinic_id):
    #person = session.query(Person).filter_by(id=person_id).one()
    #if request.method == 'POST':
        #newVisit = Visit(date=request.form['date'], arrangements=request.form[
            #'arrangements'], person_id=person_id, user_id=person.user_id)
        #session.add(newVisit)
        #session.commit()
        #flash('Новый визит от %s числа успешно добавлен' % (newVisit.date))
        #return redirect(url_for('showVisits', person_id=person_id, clinic_id=clinic_id, region_id=region_id))
    #else:
        #return render_template('nvisit.html', person_id=person_id, person=person)


# Edit a Element
#@app.route('/regions/<int:region_id>/clinics/<int:clinic_id>/persons/<int:person_id>/visits/<int:visit_id>/edit', methods=[
    #'GET', 'POST'])
#@login_required
#def editVisit(person_id, region_id, clinic_id, visit_id):
    #editedVisit = session.query(Visit).filter_by(id=visit_id).one()
    #person = session.query(Person).filter_by(id=person_id).one()
    #if request.method == 'POST':
        #if request.form['date']:
            #editedVisit.date = request.form['date']
        #if request.form['arrangements']:
            #editedVisit.arrangements = request.form['arrangements']
        #session.add(editedVisit)
        #session.commit()
        #flash('Визит успешно отредактирован')
        #return redirect(url_for('showVisits', person_id=person_id, clinic_id=clinic_id, region_id=region_id))
    #else:
        #return render_template(
            #'evisit.html', person_id=person_id, clinic_id=clinic_id, region_id=region_id,
            #visit_id=visit_id, visit=editedVisit, person=person)


# Delete a Element
#@app.route('/regions/<int:region_id>/clinics/<int:clinic_id>/persons/<int:person_id>/visits/<int:visit_id>/delete', methods=['GET', 'POST'])
#@login_required
#def deleteVisit(person_id, region_id, clinic_id, visit_id):
    #person = session.query(Person).filter_by(id=person_id).one()
    #visitToDelete = session.query(Visit).filter_by(id=visit_id).one()
    #if request.method == 'POST':
        #session.delete(visitToDelete)
        #session.commit()
        #flash('Визит успешно удален')
        #return redirect(url_for('showVisits', person_id=person_id, clinic_id=clinic_id, region_id=region_id))
    #else:
        #return render_template(
            #'dvisit.html', visit=visitToDelete, person=person, clinic_id=clinic_id, region_id=region_id)
