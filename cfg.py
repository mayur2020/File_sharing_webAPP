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



app.config["MONGO_URI"]="mongodb://localhost:27017/mycloud"
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key='bvsdhvbwbvubwuandsoowv'
app = Flask(__name__)
mongo=PyMongo(app)
