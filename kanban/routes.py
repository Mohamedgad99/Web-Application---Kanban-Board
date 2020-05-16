#Importing all the needed libraries and
#functions from different code files

from flask import render_template, url_for, redirect, request
from kanban import app, db, bcrypt
from kanban.models import Todo, User
import os
from kanban.forms import Tasks, Signupform, LoginForm
from sqlalchemy import and_, or_, not_
from flask_login import login_user, current_user, logout_user, login_required


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

#This function is what redirects users to the login page
@app.route("/", methods=['POST', 'GET'])
@login_required
def maintemp():
	todos = Todo.query.filter_by(do=False, done=False, user_id=current_user.id).all()
	dos = Todo.query.filter_by(do=True, done=False, user_id=current_user.id).all()
	dones = Todo.query.filter_by(do=True, done=True, user_id=current_user.id).all()
	return render_template('maintemp.html', todos=todos, dos=dos, dones=dones)

#Adding tasks to the todo list
#This function is what redirects the users to the adding tasks forms
#where they can add their tasks and dates
@app.route("/add", methods=['POST', 'GET'])
@login_required
def task_todo():
	form = Tasks()
	if form.validate_on_submit():
		todo = Todo(title=form.title.data, description=form.description.data, deadline=form.deadline.data, creator=current_user)
		db.session.add(todo)
		db.session.commit()
		return redirect(url_for('maintemp'))
	return render_template('task.html', form=form, title="Add Todo")

#The functions here allow the user to shuffle the tasks among
#the different categories, whether the task is done, not done, or in progress
#of being done

@app.route("/do/<int:todo_id>")
def do(todo_id):
	todo = Todo.query.get_or_404(todo_id)
	todo.do = True
	todo.done = False
	db.session.commit()
	return redirect(url_for('maintemp'))

@app.route("/done/<int:todo_id>")
def done(todo_id):
	todo = Todo.query.get_or_404(todo_id)
	todo.do = True
	todo.done = True
	db.session.commit()
	return redirect(url_for('maintemp'))

@app.route("/todo/<int:todo_id>")
def todo(todo_id):
	todo = Todo.query.get_or_404(todo_id)
	todo.do = False
	todo.done = False
	db.session.commit()
	return redirect(url_for('maintemp'))

@app.route("/elements/<int:todo_id>")
def elements(todo_id):
	todo = Todo.query.get_or_404(todo_id)
	return render_template('elements.html', todo=todo, title=f"Todo Item: {todo.title}")

#When the task is under the done category, the user will need to get rid of it
#That's what this function does, as it allows the user to either delete the task
#or put it back under the in progress section.

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
	todo = Todo.query.get_or_404(todo_id)
	db.session.delete(todo)
	db.session.commit()
	return redirect(url_for('maintemp'))



# This is the primary function responsible for registering new users
#The function will return an error message if the passwords don't match
#asking the user to fix that with a popup
#or also if the user email address already exists, and the user forgot

@app.route("/register", methods=['GET', 'POST'])
def register():
	form = Signupform()
	if form.validate_on_submit():
		# generate hashed password
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		return redirect(url_for('maintemp'))
	return render_template('register.html', title="Register", form=form)

#This function is the one responsible for users logging in
#to their personalized kanban boards
#If you are not logged in, or even signed up in the system, an error message
#will be displayed, telling you that you are not signed up, and need to do it

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('maintemp'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			next_page = request.args.get('next') #If the user was in a page before logging in
			return redirect(next_page) if next_page else redirect(url_for('maintemp'))

	return render_template('login.html', title="Login", form=form)

#This function is the ones responsible for logging users out
@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('maintemp'))
