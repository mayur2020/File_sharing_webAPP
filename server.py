from flask import Flask,abort,render_template,url_for, request, session, redirect,session
from flask_pymongo import PyMongo
import json
from datetime import datetime
from hashlib import sha256
import string
import random
from numpy.ma.core import size
import requests
import pymongo
from boto import file, file
import os
from flask.debughelpers import DebugFilesKeyError



app = Flask(__name__)

app.config["MONGO_URI"]="mongodb://localhost:27017/mycloud"
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key='bvsdhvbwbvubwuandsoowv'
mongo=PyMongo(app)

@app.route('/')
def login():
    if not 'userToken' in session:
        session['error']='Must Login To Access Homepage'
        return redirect('/login')

    token_doc = mongo.db.User_Tokens.find_one({
        'sessionHash': session['userToken'],
    })
    if token_doc is None:
        session.pop('userToken',None)
        session['error']='invalid token or you must have to login'
        return redirect('/login')
  
    error=''
    if 'error' in session:
        error = session['error']
        session.pop('error',None)

    signupSuccess=''
    if 'signupSuccess' in session:
        signupSuccess = session['signupSuccess']
        session.pop('signupSuccess',None)

    userId = token_doc['userId']

    user = mongo.db.users.find_one({
        '_id': userId
    })

    uploaded_files = mongo.db.Files.find({
        'user_Id': userId,
        'isActive': True
    }).sort([("createdAt", pymongo.DESCENDING)])


    return render_template('/profile.html',uploaded_files=uploaded_files,user=user,error=error,signupSuccess=signupSuccess)
    
@app.route('/home')
def home():
    return render_template('/profile.html')


@app.route('/signup')
def show_signup():
    error=''
    if 'error' in session:
        error = session['error']
        session.pop('error',None)
    return render_template('signup.html' ,error=error)


@app.route('/login')
def signup():
    error=''
    if 'error' in session:
        error = session['error']
        session.pop('error',None)
 
    signupSuccess=''
    if 'signupSuccess' in session:
        signupSuccess = session['signupSuccess']
        session.pop('signupSuccess',None)   
    return render_template('login.html',error=error,signupSuccess=signupSuccess)




@app.route('/check_login',methods=['POST'])
def check_login():
    email = request.form['email']
    password = request.form['password']  
    if not len(email) > 0:
        session['error'] = 'Please Enter Email'
        return redirect('/login')

    if not '@' in email or not '.' in email:
        session['error']='Email is invalid'
        return redirect('/login')

    if not len(password) > 0:
        session['error']='Password is required'
        return redirect('/login')

    user_doc = mongo.db.users.find_one({ "email":email })
    if user_doc is None:
        session['error']='No account exist with this email'
        return redirect('/login')

    password_hash = sha256(password.encode('utf-8')).hexdigest()
    if user_doc['password'] != password_hash:
        session['error'] = 'password is wrong'
        return redirect('/login')
    
    def get_random_string(str_size=10):
        allowed_char =  string.ascii_letters + string.punctuation
        return ''.join(random.choice(allowed_char) for x in range(str_size))

    random_string = get_random_string() 
    randomSessionHash = sha256(random_string.encode('utf-8')).hexdigest()    
    token_object = mongo.db.User_Tokens.insert_one({
        'userId': user_doc['_id'],
        'sessionHash': randomSessionHash,
        'createdAt': datetime.utcnow(),
    })

    session['userToken'] = randomSessionHash
    return redirect('/')




@app.route('/handle_signup',methods=['POST'])
def handle_signup():
    email = request.form.get('email')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')

    if not len(email) > 0:
        session['error'] = 'Please enter email'
        return redirect('/signup')

    if not '@' in email or not '.' in email:
        session['error']='Email is invalid'
        return redirect('/signup')

    if not len(password) > 0:
        session['error']='Password is required'
        return redirect('/signup')

    if password != cpassword:
        session['error']='Both the Passwords must be same'
        return redirect('/signup')

    match_user = mongo.db.users.count_documents({"email": email})
    if match_user > 0:
        session['error']='User is already exists'
        return redirect('/signup')

    password = sha256(password.encode('utf-8')).hexdigest()
    cpassword = sha256(cpassword.encode('utf-8')).hexdigest()
    result = mongo.db.users.insert_one({
        'email': email,
        'password': password,
        'cpassword': cpassword,
        'name': '',
        'lastLoginDate': None,
        'createdAt': datetime.utcnow(),
        'updatedAt': datetime.utcnow(),
    })   
    session['signupSuccess']='Your account is ready to login'
    return redirect('/login')


@app.route('/logout')
def logout():
    return redirect('/login')


def allowed_file(filename):
    ALLOWED_EXTENSION = ['jpg','jpeg','png','gif','doc','docx','xls','xlsx','ppt','pptx','pdf','csv']
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION


@app.route('/handle_file_upload', methods=['POST'])
def handle_file():
    if not 'userToken' in session:
        session['error']='Must Login To Access Homepage'
        return redirect('/login')

    token_doc = mongo.db.User_Tokens.find_one({
        'sessionHash': session['userToken'],
    })
    if token_doc is None:
        session.pop('userToken',None)
        session['error']='invalid token or you must have to login'
        return redirect('/login')
    
    file = request.files['uploadedFile']

    if file.filename == '':
        session['error']='Please select the file'
        return redirect('/')

    if not allowed_file(file.filename):
        session['error']='File type not allowed'
        return redirect('/')


    if 'uploadedFile' not in request.files:
        session['error']='No file uploaded by the user'
        return redirect('/')


    filename = secure_filename = (file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    filepath = file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    extension = filename.rsplit('.', 1)[1].lower()
    userId = token_doc['userId']
    result = mongo.db.Files.insert_one({
        'user_Id': userId,
        'originalFileName': file.filename,
        'fileType': extension,
        'fileSize': 0,
        'fileHash': 0,
        'filePath': filepath,
        'isActive': True,
        'createdAt': datetime.utcnow(),
    })
    session['signupSuccess']='Your file is uploaded successfully...!'
    return redirect('/')


if __name__ == '__main__':
    app.run()