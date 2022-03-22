from re import S
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates')

students = {}

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    return render_template('main.html', message="Hello! This is the main page.")

@app.route("/posts/create", methods=['GET', 'POST'])
def posts_create():
    if ('name' in request.form and 'email' in request.form):
        name = request.form['name']
        email = request.form['email']

        students[name] = email

    return render_template('create.html', message="You can create new posts here")

@app.route("/posts", methods=['GET', 'POST'])
def posts():
    return render_template('posts.html', message="You can find the list of posts here", students_list=students)