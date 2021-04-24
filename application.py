import os
import sys
from flask import Flask, session, render_template, redirect, url_for, request,session,jsonify,abort
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import psycopg2
from form import RegisterForm, LoginForm
import json
import requests




app = Flask(__name__)
app.config['SECRET_KEY']='7ff61fae7049489'
os.environ["DATABASE_URL"] = "postgresql://postgres:BaMyY1&5@localhost:5432/book_read"


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/index")
@app.route("/")
def index():
    
    search = request.args.get('search')
    value = str(request.args.get('value'))
    response = ""
    volumes = []
    i = ""
    # checks if profile data exist in session 
    if 'username' in session:
        if(search):
            
            try:
                
                response = db.execute(f"SELECT isbn FROM books WHERE\
                                        title LIKE '%{value}%' OR\
                                        isbn LIKE '%{value}%' OR\
                                        author LIKE '%{value}%' LIMIT 9; ").fetchall()
                isbns = [item for t in response for item in t]
                
                for isbn in isbns:
                    r = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={isbn}").json()
                    i = isbn 
                    if r != None and ("items" in r):
                        items = r["items"]
                        
                        item = items[0]['volumeInfo']
                        item["isbn"] = isbn
                        volumes.append(item)
                    else:
                        break
    
            except Exception as e:
                abort(500)
            
            return render_template("index.html", volumes=volumes, fName = session['first-name'], lName = session['last-name'], email = session['email'])
        else:
            return render_template("index.html", volumes={}, fName = session['first-name'], lName = session['last-name'], email = session['email'])
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=["GET","POST"])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        passd = form.password.data 
        try:
            profile = db.execute(f"SELECT * FROM users WHERE username= '{username}' AND  passd= '{passd}' ").fetchall()
            if profile:
                session['username'] = profile[0][0]
                session['first-name'] = profile[0][1]
                session['last-name'] = profile[0][2]
                session['email'] = profile[0][3]
                return redirect(url_for('index'))

        except:
            abort(500)
        
        
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        fName = form.firstName.data
        lName = form.lastName.data
        email = form.email.data
        username = form.username.data
        psd = form.password.data
        try:
            db.execute("INSERT INTO users (username,firstname,lastname, email,passd) VALUES ( :username, :firstname, :lastname,:email,:passd)",
                {"username": username,"firstname":fName,"lastname":lName, "email": email ,"passd":psd}) 
            db.commit() 
            
            return redirect(url_for('login'))
        except :
           render_template("register.html")
    
    return render_template("register.html", form=form)

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('login'))


@app.route('/book', methods=["GET","POST"])
def book():
    isbn = str(request.args.get('isbn'))
    title = request.args.get('title')
    reviews = []
    volume = ""
    rateSum = 0
    duplicate = False
   
  

    if request.method == "POST":
       
        review = str(request.form.get('review'))
        rate = int(request.form.get('rate'))
        username = session['username']
        try:
            db.execute("INSERT INTO reviews (title,username,review, rate) VALUES ( :title, :username, :review,:rate)",
                    {"title": title,"username":username,"review":review, "rate": rate}) 
            db.commit() 
            
        except:
            abort(500)

    r = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={isbn}").json()
    if r != None and ("items" in r):
        items = r["items"]
        volume = items[0]["volumeInfo"]
        volume['isbn'] = isbn
     
    
    try:
        data = db.execute(f"SELECT * FROM reviews WHERE title= '{title}' ").fetchall()
        for review in data:
            reviews.append(review)
            rateSum += review['rate']
            if review['username'] == session['username']:
                duplicate = True
    except:
        abort(500)

  
    
    return render_template("book.html",duplicate=duplicate, reviews=reviews, volume = volume)

@app.route('/search', methods=['GET','POST'])
def search():
    #  https://www.googleapis.com/books/v1/volumes?q={search terms}
    value = str(request.form.get("search-arg"))
    return redirect(url_for('index', search=True, value = value))

@app.errorhandler(404)
def page_not_found(error):
   return render_template('error.html'), 404
    
@app.errorhandler(500)
def internal_error(error):

    return render_template('error.html'), 500
