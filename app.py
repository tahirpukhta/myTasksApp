from flask import Flask, render_template, request, redirect, jsonify, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///task.db'
app.secret_key='babubhaiya'
db=SQLAlchemy(app)

#Authentication setup
def check_auth(username,password):
    stored_username="babu" 
    stored_password="babu123"
    return username==stored_username and password==stored_password
#def authenticate():
    #return jsonify({"Error":"Authentication required"}),401
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Please log in to access this page.","warning")
            return redirect(url_for('login'))
        """auth=request.authorization
        if not auth:
            fallback to form data for authentication
            username=request.form.get('username')
            password=request.form.get('password')
            if not username or not password or not check_auth(username,password):
                return authenticate()
        else:
            # validate using authorization headers
            if not check_auth(auth.username, auth.password):
                return authenticate()"""
        return f(*args, **kwargs)
    return decorated

#Database Model
class Todo(db.Model):
    sno= db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(200), nullable=False)
    desc=db.Column(db.String(500), nullable=False)
    date_created=db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self)-> str:
        return f"{self.sno} - {self.title}"

#Different Routes
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/")
def welcome():
    allTodo=Todo.query.all()
    return render_template('index.html', allTodo=allTodo)

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if check_auth(username,password):
            session['logged_in']=True
            session['username']=username #we are storing username in the session to greet user on the my_goals page. 
            flash("Login successful!","success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.","danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

@app.route("/my_goals")
@requires_auth  # Ensure the user is authenticated
def my_goals():
    username = session.get('username', 'User')  # Get the username from the session, default to 'User'
    return render_template('my_goals.html', username=username)

@app.route("/add", methods=['POST'])
@requires_auth # restrict post access to authntic users.
def add_task():
    #if request.method=='POST':
        #print("post kaam kar raha he")
        #print(request.form['title']) #to check if our requests work.
    title=request.form['title']
    desc=request.form['desc']

    todo=Todo(title=title,desc=desc)
    db.session.add(todo)
    db.session.commit()
    flash("Task added successfully!","success")
    return redirect('/')
    #allTodo=Todo.query.all()
    #return render_template('index.html',allTodo=allTodo)
    #return "<p>Hello, World!</p>"
#keeping it for any future potential use such as use of JSON output , API developement and other uses.
@app.route("/show")
@requires_auth
def show():
    allTodo=Todo.query.all()
    #print(allTodo)
    #return "<p>You've landed on the alltodo page!</p>"
    return jsonify([{"sno": todo.sno, "title": todo.title, "desc": todo.desc} for todo in allTodo])

@app.route("/update/<int:sno>",methods=['GET', 'POST'])
@requires_auth
def update(sno):
    if request.method=='POST':
        title=request.form['title']
        desc=request.form['desc']
        todo=Todo.query.filter_by(sno=sno).first()
        todo.title=title
        todo.desc=desc
        db.session.add(todo)
        db.session.commit()
        flash("Task updated successfully!","success")
        return redirect ('/')

    todo=Todo.query.filter_by(sno=sno).first()
    return render_template('update.html',todo=todo)

@app.route("/delete/<int:sno>")
@requires_auth
def delete(sno):
    todo=Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    flash("Task deleted successfully", "success")
    return redirect('/')


if __name__=="__main__":
    is_production=os.getenv("FLASK_ENV")=="production"
    app.run(
        debug=not is_production, 
        host='0.0.0.0' if is_production else '127.0.0.1', 
        port=5000
        )


