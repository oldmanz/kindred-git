## flask run --host=0.0.0.0

from flask import Flask, request, render_template
from flask_cors import CORS
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

client = MongoClient("mongodb://root:password@db:27017/")
db = client.kindred

people = db.people

app = Flask(__name__)
CORS(app)


@app.route("/") 
def serve_main(): 
    return render_template('index.html')


@app.route("/seed")
def seed_db():
    people.drop()
    
    travis = {
        "first_name": "Travis",
        "last_name": "Zimmerman",
        "gender": "male"
    }

    travis_id = people.insert_one(travis).inserted_id
    
    hannah = {
        "first_name": "Hannah",
        "last_name": "Zimmerman",
        "gender": "female",
        "pids": [travis_id]
    }

    hannah_id = people.insert_one(hannah).inserted_id

    people.find_one_and_update({"_id": travis_id}, {'$set': {'pids': [hannah_id]}})

    barrett = {
        "first_name": "Barrett",
        "last_name": "Zimmerman",
        "gender": "male"
    }
    
    barrett_id = people.insert_one(barrett).inserted_id
    
    people.find_one_and_update({"_id": travis_id}, {'$set': {'fid': barrett_id}})

    return "Done!"

@app.route("/people")
def get_family():
    family = []
    for person in people.find():
        person['name'] = "{} {}".format(person['first_name'], person['last_name'])
        person['id'] = person['_id']
        if 'edit_history' in person:
            person.pop('edit_history')
        family.append(person)
    return json.dumps(family, default=str)

@app.route("/save", methods = ['POST'])
def save_person():
    new_datas = request.json['updateNodesData']
    for new_data in new_datas:
        _id = ObjectId(new_data['_id'])
        new_data.pop('_id')
        old_data = people.find_one({'_id':_id})

        edit_history = []
        if 'edit_history' in old_data:
            edit_history = old_data['edit_history']

        old_data['date_changed'] = datetime.datetime.now()

        old_data.pop('edit_history')

        edit_history.append(old_data)
        
        new_data['edit_history'] = edit_history

        people.find_one_and_update({"_id":_id}, {'$set': new_data})
    return {"success": True}