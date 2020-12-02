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