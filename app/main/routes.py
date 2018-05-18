from datetime import datetime, timedelta
from flask import render_template, flash, redirect, request,\
    url_for, send_from_directory, jsonify, current_app
from app import db
from app.main.forms import  EditProfileForm, PostForm, AddInfo
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Post, User, Clinic, Tender, Contract, Person, DoNotForget
from app.main import bp



@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = AddInfo()
    if form.validate_on_submit():
        info = DoNotForget(notes=form.notes.data, author=current_user)
        db.session.add(info)
        db.session.commit()
        return redirect(url_for('main.index'))
    infos = DoNotForget.query.filter_by(user_id=current_user.id).all()
    tenders = Tender.query.filter_by(user_id=current_user.id).filter(Tender.game_date >= datetime.today()).order_by(Tender.end_date.asc()).all()
    contracts = Contract.query.filter_by(user_id=current_user.id).filter(Contract.sign_date >= datetime.today()).order_by(Contract.sign_date.asc()).all()
    persons = Person.query.filter_by(user_id=current_user.id).filter(Person.next_visit > datetime.today()).order_by(Person.next_visit.asc()).all()
    return render_template('index.html', title='Home', tenders=tenders, persons=persons, form=form, infos=infos, contracts=contracts)

@bp.route('/del/<int:info_id>', methods=['GET', 'POST'])
@login_required
def deleteInfo(info_id):
    infoToDelete = DoNotForget.query.filter_by(id=info_id).one()
    db.session.delete(infoToDelete)
    db.session.commit()
    return redirect(url_for('main.index'))

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




@bp.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Ваше сообщение опубликовано')
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("chat.html", title='Explore', posts=posts.items, form=form,
                          next_url=next_url, prev_url=prev_url)


@bp.route('/delete/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    postToDelete = Post.query.filter_by(id=post_id).one()
    db.session.delete(postToDelete)
    db.session.commit()
    flash('Сообщение было удалено')
    return redirect(url_for('main.explore'))
