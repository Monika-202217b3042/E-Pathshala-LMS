from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db
from .models import User, Course, Enrollment

main = Blueprint('main', __name__)

def get_current_user():
    """Helper function to get the currently logged-in user."""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

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
        courses = Course.query.filter_by(instructor_id=user.id).all()
        total_courses = len(courses)
        student_ids = set()
        total_enrollments = 0

        for course in courses:
            enrollments = Enrollment.query.filter_by(course_id=course.id).all()
            total_enrollments += len(enrollments)
            for enrollment in enrollments:
                student_ids.add(enrollment.student_id)
        total_students = len(student_ids)

        return render_template(
            'instructor_dashboard.html', 
            user=user, 
            courses=courses,  
            total_students=total_students,
            total_courses=total_courses, 
            total_enrollments=total_enrollments
        )
    else:
        courses_data = [(enrollment.course, enrollment.progress) for enrollment in user.enrollments]
        available_courses = Course.query.filter(Course.id.notin_([en.course_id for en in user.enrollments])).all()

        return render_template(
            'student_dashboard.html', 
            user=user, 
            courses=courses_data,
            available_courses=available_courses  
        )

    return render_template(template, user=user, courses=courses)
    
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('main.dashboard'))  # Removed flash message
        flash("Invalid username or password", "danger")
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
    session.clear()
    return redirect(url_for('main.index'))

@main.route('/create-course', methods=['GET', 'POST'])
def create_course():
    user = get_current_user()
    if not user or not user.is_instructor:
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

@main.route('/enroll_in_course/<int:course_id>', methods=['POST'])
def enroll_in_course(course_id):
    user = get_current_user()
    if not user:
        flash("Please log in first.", "warning")
        return redirect(url_for('main.login'))

    course = Course.query.get_or_404(course_id)
    if not Enrollment.query.filter_by(student_id=user.id, course_id=course.id).first():
        enrollment = Enrollment(student_id=user.id, course_id=course.id, progress=0)
        db.session.add(enrollment)
        db.session.commit()
        flash("You have been enrolled in the course!", "success")
    else:
        flash("You are already enrolled in this course.", "info")
    
    return redirect(url_for('main.dashboard'))

@main.route('/courses')
def courses():
    user = get_current_user()
    if not user or not user.is_instructor:
        flash("Unauthorized! Only instructors can create courses.", "danger")
        return redirect(url_for('main.dashboard'))

    courses = Course.query.filter_by(instructor_id=user.id).all()
    return render_template('courses.html', courses=courses)



@main.route('/students')
def students():
    user = get_current_user()
    if not user or not user.is_instructor:
        flash("Unauthorized! Only instructors can create courses.", "danger")
        return redirect(url_for('main.dashboard'))
    
    # Fetch all unique students from the instructor’s courses
    student_ids = {enrollment.student_id for course in user.courses for enrollment in course.enrollments}
    students = User.query.filter(User.id.in_(student_ids)).all()
    
    return render_template('students.html', students=students)

@main.route('/enrollments')
def enrollments():
    user = get_current_user()
    if not user or not user.is_instructor:
        flash("Unauthorized! Only instructors can create courses.", "danger")
        return redirect(url_for('main.dashboard'))
    
    # Get enrollments specific to this instructor by checking courses taught by the instructor
    enrollments = Enrollment.query.filter(Enrollment.course.has(instructor_id=user.id)).all()
    
    return render_template('enrollments.html', enrollments=enrollments)

@main.route('/profile')
def profile():
    user = get_current_user()
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    user = User.query.get(session['user_id'])  # Fetch user from database
    return render_template('profile.html', user=user)

@main.route('/course_dashboard')
def course_dashboard():
    if 'user_id' not in session:
        flash("Please log in to view this page.")
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    if user is None:
        flash('User not found. Please log in again.')
        return redirect(url_for('main.login'))
    
    available_courses = Course.query.filter(Course.id.notin_([en.course_id for en in user.enrollments])).all()
    return render_template('course_dashboard.html', available_courses=available_courses) 

@main.route('/course_detail/<int:course_id>')
def course_detail(course_id):
    if 'user_id' not in session:
        flash("Please log in to view this page.")
        return redirect(url_for('main.login'))
    
    user = User.query.get(session['user_id'])
    course = Course.query.get_or_404(course_id)
    if not any(enrollment.course_id == course.id for enrollment in user.enrollments):
        flash("You are not enrolled in this course.", "warning")
        return redirect(url_for('main.dashboard'))
    
    return render_template('course_detail.html', course=course, user=user)