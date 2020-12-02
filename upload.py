from flask import Flask,abort,render_template,redirect
from flask_pymongo import PyMongo
import pymongo
import request


app = Flask(__name__)

app.config["MONGO_URI"]="mongodb://localhost:27017/student"
mongo=PyMongo(app)

@app.route('/handle_data',methods=['POST'])
def handle_file():
    if request.method == 'POST':
        grno = request.form['id']
        name = request.form['name']
        gen = request.form['gen']
        gen1 = request.form['gen1']
        age = request.form['age']
        course = request.form['course']
        sem = request.form['sem']

        result = mongo.db.user.insert_one({
        'GR_No': grno,
        'Name': name,
        'Gender': gen,
        'Age': age,
        'Course': course,
        'Semester': sem,
        })

        if result:
            return render_template('home.html')
        else:
            print("Error...!")
    else:
        print("Error...!")

    
