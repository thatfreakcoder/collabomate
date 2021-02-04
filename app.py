#!/usr/bin/python3.6

from flask import Flask, request, jsonify, render_template, session, redirect, flash
from flask_mysqldb import MySQL
from os import urandom
from yaml import load, FullLoader
from datetime import datetime

app = Flask(__name__)
mysql = MySQL(app)

# MySQL Configuration
db_keeps = load(open('db.yaml'), Loader=FullLoader)
app.config['MYSQL_HOST'] = db_keeps['mysql_host']
app.config['MYSQL_USER'] = db_keeps['mysql_user']
app.config['MYSQL_PASSWORD'] = db_keeps['mysql_password']
app.config['MYSQL_DB'] = db_keeps['mysql_db']
app.config['SECRET_KEY'] = urandom(24)

@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization, data')
    return response

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    q = cur.execute("SELECT * FROM open_projects;")
    if q > 0:
        projects = cur.fetchall()
        return render_template('my_index.html', projects=projects)
    else:
        return jsonify({'response' : 'error', 'message': "No Database Entries Found", 'keeps': int(q)})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        session['logged_in'] = True
        session['user_id'] = 1
        return redirect('/')

@app.route('/project/<int:id>')
def project(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM open_projects WHERE project_id={};".format(id))
    info = cur.fetchone()
    return render_template('project.html', info=info)

@app.route('/project/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        response = request.form
        title = response['title']
        description = response['description']
        owner_id = session['user_id']
        date = now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        links = response['links']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO open_projects(title, description, owner_id, date, links) VALUES(%s, %s, %d, %s, %s);", (title, description, owner_id, date, links))
        mysql.connection.commit()
        cur.close
        flash("Projects Created Successfully", "success")
        return redirect('/')
    return render_template('/create.html')

@app.route('/profile/me')
def me():
    id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM profile WHERE user_id={};".format(id))
    q = cur.fetchone()
    return render_template('profile.html', profile=q)

@app.route('/profile/<reg_no>')
def profile(reg_no):
    reg_no = str(reg_no).upper()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM profile WHERE registration_number='{}';".format(reg_no))
    q = cur.fetchone()
    print(q)
    return render_template('profile.html', profile=q)

@app.route('/assignments')
def assignments():
    return None

@app.errorhandler(404)
def error(e):
    return jsonify({
        'response'  : 'failure',
        'error'     : '404',
        'message'   : str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)