from flask import Flask,abort,render_template,url_for, request,send_file, abort, session, redirect,session
from flask_pymongo import PyMongo
import json
from datetime import datetime
from hashlib import sha256
import string
import hashlib
import random
from numpy.ma.core import size
import requests
import pymongo
from boto import file, file
import os
from flask.debughelpers import DebugFilesKeyError
from fileinput import filename
import smtplib
import urllib.request
import webbrowser
from pathlib import Path
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from os import path
from bson import ObjectId
from pathlib import Path
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

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

    info=''
    if 'info' in session:
        info = session['info']
        session.pop('info',None)

    userId = token_doc['userId']

    user = mongo.db.users.find_one({
        '_id': userId
    })

    uploaded_files = mongo.db.Files.find({
        'user_Id': userId,
        'isActive': True
    }).sort([("createdAt", pymongo.DESCENDING)])

    return render_template('/profile.html',uploaded_files=uploaded_files,user=user,error=error,signupSuccess=signupSuccess,info=info)

    
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
    now = datetime.now()
    result = mongo.db.users.insert_one({
        'email': email,
        'password': password,
        'cpassword': cpassword,
        'name': email,
        'lastLoginDate': None,
        'createdAt': now.strftime("%d/%m/%Y  %H:%M:%S"),
        'updatedAt': now.strftime("%d/%m/%Y  %H:%M:%S"),
    })   
    session['signupSuccess']='Your account is ready to login'
    return redirect('/login')


@app.route('/logout')
def logout():
    token = session['userToken'] 
    print(token)
    us = mongo.db.User_Tokens.remove({
        'sessionHash': token
    })
    if us:
        print("success")

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


    filename = (file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
   
    print(filepath)
    extension = filename.rsplit('.', 1)[1].lower()
    userId = token_doc['userId']
    now = datetime.now()
    ss=os.path.getsize(filepath)
    print(ss)
    if ss < 1024*1024 :
        size_kb = str(ss/1024)
        size = str(size_kb[:3])+ ' ' + 'KB'    
    else:
        size_mb= str(ss/1024/1024)
        size=str(size_mb[:3]) +' '+ 'MB'

 
    hasher = hashlib.md5()
    with open(filepath, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    filehash=hasher.hexdigest()      
        

    try:
        result = mongo.db.Files.insert_one({
        'user_Id': userId,
        'originalFileName': file.filename,
        'fileType': extension,
        'fileSize': size,
        'fileHash': filehash,
        'filePath': filepath,
        'isActive': True,
        'createdAt': now.strftime("%d/%m/%Y  %H:%M:%S"),
    })
    except:
        session['error']='Something went wrong...!'
    session['signupSuccess']='Your file uploaded successfully...!'
    return redirect('/')


@app.route('/share/<_id>/<originalFileName>', methods=["GET"])
def Sharing(_id,originalFileName):
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
        
    if not 'userToken' in session:
        session['error']='Must Login To Access Homepage'
        return redirect('/login')

    info=''
    if 'info' in session:
        info = session['info']
        session.pop('info',None)


    fromaddr = 'mayur137137@gmail.com'
    toaddr = 'mayur.mane18@vit.edu' 
    msg = MIMEMultipart() 

    msg['From'] = fromaddr  
    msg['To'] = toaddr 
 
    msg['Subject'] = "Document" 
    body = "I'm sharing some document's with please go throgh that"

    msg.attach(MIMEText(body, 'plain'))  
    filename = originalFileName
    attachment = open("uploads/"+ filename , "rb") 
    p = MIMEBase('application', 'octet-stream') 
    
    p.set_payload((attachment).read()) 
    encoders.encode_base64(p) 

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)  
    msg.attach(p) 
 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
 
    s.login(fromaddr, "Mayur@1234567890") 

    text = msg.as_string()  
    s.sendmail(fromaddr, toaddr, text) 
 
    s.quit()

    session['info']='Mail Send successfully...!' 
    return redirect('/')



@app.route('/download_file/<_id>', methods=["GET"])
def downloadFile(_id):
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

    file_object = mongo.db.Files.find_one({
        '_id': ObjectId(_id)
    })

    if file_object is None:
        return abort(404)
    
    userId = token_doc['userId']
    mongo.db.File_Downloads.insert_one({
        'fileId': file_object['_id'],
         'userId': userId,
         'createdAt': datetime.now()
    })
    filepath = file_object['filePath']
    return send_file(filepath, as_attachment=True)
    return redirect('/')

@app.route('/delete/<originalFileName>', methods=['GET','POST'])
def deleteFile(originalFileName):
    file_name=originalFileName
    delete_file = mongo.db.Files.remove({
        'originalFileName': file_name
    })
    if delete_file:
        session['info']='Your File Deleted successfully...!'
    else:
        session['error']= 'File Not deleted...!'
    return redirect('/')

if __name__ == '__main__':
    app.run()