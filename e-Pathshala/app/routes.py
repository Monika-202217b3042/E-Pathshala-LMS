from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db
from .models import User, Course, Enrollment

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to view this page.")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    if user is None:
        flash('User not found. Please log in again.')
        return redirect(url_for('main.login'))

    if user.is_instructor:
        courses = user.courses
        template = 'instructor_dashboard.html'
    else:
        enrolled_courses = Enrollment.query.filter_by(student_id=user.id).all()
        courses = []

        for enrollment in enrolled_courses:
            course = Course.query.get(enrollment.course_id)
            courses.append({"title": course.title, "progress": enrollment.progress})

        template = 'student_dashboard.html'

    return render_template(template, user=user, courses=courses)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['logged_in'] = True
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect(url_for('main.dashboard'))
        
        flash('Invalid username or password', "danger")
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_instructor = 'is_instructor' in request.form

        new_user = User(username=username, password=password, is_instructor=is_instructor)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('main.index'))

@main.route('/create-course', methods=['GET', 'POST'])
def create_course():
    if not session.get('user_id'):
        flash("Please log in first.", "warning")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    if not user.is_instructor:
        flash("Unauthorized! Only instructors can create courses.", "danger")
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        course = Course(title=title, description=description, instructor_id=user.id)
        db.session.add(course)
        db.session.commit()
        
        flash("Course created successfully!", "success")
        return redirect(url_for('main.dashboard'))

    return render_template('create_course.html')

@main.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        course.title = request.form['title']
        course.description = request.form['description']
        db.session.commit()
        flash("Course updated successfully!", "success")
        return redirect(url_for('main.dashboard'))
    return render_template('edit_course.html', course=course)

@main.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted successfully!", "success")
    return redirect(url_for('main.dashboard'))

@main.route('/enroll_in_course/<int:course_id>', methods=['GET', 'POST'])
def enroll_in_course(course_id):
    if 'user_id' not in session:
        flash("Please log in to view this page.", "warning")
        return redirect(url_for('main.login'))

    current_user = User.query.get(session['user_id'])
    if current_user is None:
        flash('User not found. Please log in again.', "danger")
        return redirect(url_for('main.login'))

    course = Course.query.get_or_404(course_id)
    is_enrolled = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()

    if not is_enrolled:
        enrollment = Enrollment(student_id=current_user.id, course_id=course.id, progress=0)
        db.session.add(enrollment)
        db.session.commit()
        flash('You have been enrolled in the course!', "success")
    else:
        flash('You are already enrolled in this course.', "info")

    return redirect(url_for('main.dashboard'))
