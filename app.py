#Flask installs
from flask import Flask, request, jsonify
from flask_heroku import Heroku
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS


import os

#Grabbing APIs
import requests
from requests.api import head

#To get tiktok followers
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

#Secret Keys
import secret

# Twitter, Tiktok, and Instagram - Followers
# Twitch and Youtube - Followers and weekly views

app = Flask(__name__)
driver = webdriver.Chrome(ChromeDriverManager().install())

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')


heroku = Heroku(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    instagram = db.Column(db.String(), nullable=True)
    tiktok = db.Column(db.String(), nullable=True)
    twitch = db.Column(db.String(), nullable=True)
    twitter = db.Column(db.String(), nullable=True)
    youtube = db.Column(db.String(), nullable=True)

    def __init__(self, name, instagram, tiktok, twitch, twitter, youtube):
        self.name = name
        self.instagram = instagram
        self.tiktok = tiktok
        self.twitch = twitch
        self.twitter = twitter
        self.youtube = youtube

class UserSchema(ma.Schema):
    class Meta:
        fields = ["id", "name", "instagram", "tiktok", "twitch", "twitter", "youtube"]

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route('/user/add', methods=['POST'])
def add_user():
    if request.content_type == "application/json":
        post_data = request.get_json()
        name = post_data.get('name')
        instagram = post_data.get('instagram')
        tiktok = post_data.get('tiktok')
        twitch = post_data.get('twitch')
        twitter = post_data.get('twitter')
        youtube = post_data.get('youtube')

        record = User(name, instagram, tiktok, twitch, twitter, youtube)
        db.session.add(record)
        db.session.commit()

        return jsonify('User has been created')
    return jsonify('Request must be sent as JSON data')

@app.route('/user/edit/<id>', methods=['PUT'])
def edit_user(id):
    if request.content_type == "application/json":
        post_data = request.get_json()
        user = User.query.filter_by(id=id).first()

        if user is None:
            return jsonify('There is no User')

        if post_data.get('name') is not None: user.name = post_data.get('name')
        if post_data.get('instagram') is not None: user.instagram = post_data.get('instagram')
        if post_data.get('tiktok') is not None: user.tiktok = post_data.get('tiktok')
        if post_data.get('twitch') is not None: user.twitch = post_data.get('twitch')
        if post_data.get('twitter') is not None: user.twitter = post_data.get('twitter')
        if post_data.get('youtube') is not None: user.youtube = post_data.get('youtube')

        db.session.commit()

        return jsonify('User edited')
    return jsonify('Request must be sent as JSON data')

@app.route('/user/get', methods=['GET'])
def get_users():
    users = db.session.query(User).all()
    return jsonify(users_schema.dump(users))

@app.route('/user/delete/<id>', methods=['DELETE'])
def delete_user(id):
    to_delete = db.session.query(User).filter(User.id == id).first()
    if to_delete is None: return jsonify('User does not exist')
    db.session.delete(to_delete)
    db.session.commit()
    return jsonify('User deleted successfully')


# CRUD completed, now we're grabbing stats from different APIs

@app.route('/twitter/<username>')
def twitter_stats(username):
    api_url = f'https://api.twitter.com/2/users/by/username/{username}'
    headers = {'Authorization': f'Bearer {secret.bearer_token}'}
    response = requests.get(api_url, headers=headers)
    id = response.json()["data"]["id"]

    api_url = f'https://api.twitter.com/2/users/{id}/followers'
    response = requests.get(api_url, headers=headers)
    return jsonify(response.json())

@app.route('/tiktok/<username>')
def tiktok_stats(username):
    driver.get(f'https://www.tiktok.com/@{username}?lang=en')
    followers = driver.find_element_by_xpath('//*[@id="main"]/div[2]/div[2]/div/header/h2[1]/div[2]/strong').text

    return followers



if __name__ == "__main__":
    app.run(debug=True)