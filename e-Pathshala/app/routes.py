from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db
from .models import User, Course

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    if not 'user_id' in session:
        flash("Please log in to view this page.")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    if user.is_instructor:
        courses = user.courses
    else:
        courses = Course.query.all()

    return render_template('dashboard.html', user=user, courses=courses)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['logged_in'] = True
            session['user_id'] = user.id
            return redirect(url_for('main.dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_instructor = 'instructor' in request.form

        new_user = User(username=username, password=password, is_instructor=is_instructor)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('main.index'))

@main.route('/create_course', methods=['GET', 'POST'])
def create_course():
    if not session.get('logged_in'):
        return redirect(url_for('.login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        instructor_id = session['user_id']  # assuming this is stored in session upon login

        course = Course(title=title, description=description, instructor_id=instructor_id)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('.dashboard'))

    return render_template('create_course.html')

@main.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        course.title = request.form['title']
        course.description = request.form['description']
        db.session.commit()
        return redirect(url_for('.dashboard'))
    return render_template('edit_course.html', course=course)

@main.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('.dashboard'))