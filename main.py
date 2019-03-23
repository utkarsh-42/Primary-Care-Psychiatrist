from flask import Flask
#for language api
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
#for chart
from flask import Markup
from flask import render_template
#for database
from flask import request, session, make_response, url_for, redirect
from models.user import User
from models.chart import Chart
from common.database import Database
from pymongo import MongoClient


app = Flask(__name__)
app.secret_key = "arrow"

mongo_object = MongoClient()
db = mongo_object['hackathon']
collection = db['analyze']


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/login')
def login_template():
    return render_template('new_login.html')


@app.route('/register')
def register_template():
    return render_template('register.html')


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    if User.login_valid(email, password):
        User.login(email)
    else:
        session['email'] = None

    user = User.get_by_email(email)
    return render_template("profile.html", email=session['email'], name=user.name)


@app.route('/logout', methods=['POST'])
def logout():
    session['email'] = None

    render_template("profile.html", email=session['email'], name=name)

@app.route('/doctor')
def doctor():
    return render_template("doctor.html")

@app.route('/auth/register', methods=['POST'])
def register_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    User.register(name, email, password)

    return render_template("profile.html", email=session['email'], name=name)

@app.route('/analyze/<string:user_id>')
@app.route('/analyze')
def user_analyze(user_id=None):

    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_email(session['email'])

    analyze = user.get_analyze()

    return render_template("user_analyze.html", analyze=analyze, email=user.email, name=user.name)

@app.route('/analyze/new', methods=['POST', 'GET'])
def create_new_blog():
    if request.method == 'GET':
        return render_template('new_analyze.html')
    else:
        description = request.form['description']
        user = User.get_by_email(session['email'])

        new_analyze = Chart(user.name, user.email, description, user._id)
        new_analyze.save_to_mongo()

        return make_response(user_analyze(user._id))

#@app.route('/chart/<string:user_id>')
#@app.route('/chart/<string:email>')
@app.route('/chart')
def chart():
    

    user = User.get_by_email(session['email'])
    print(type(user))


    data = user.get_analyze()
    print(type(data))

    mylist = []

    for dat in data:
        mylist.append(dat['description'])

    client = language.LanguageServiceClient()

    myscore=[]

    for i in mylist:
    # The text to analyze
        text = i
        document = types.Document(
                    content=text,
                    type=enums.Document.Type.PLAIN_TEXT)

        # Detects the sentiment of the text
        sentiment = client.analyze_sentiment(document=document).document_sentiment
        myscore.append(sentiment.score)
    #print('Text: {}'.format(text))
    #print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))




    values = myscore
    print(values)

    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" ];
   
    return render_template('chart.html', values=values, labels=labels)

    
if __name__ == '__main__':
    app.secret_key = 'hackathon'
    app.run(debug=True,host='0.0.0.0',port='8000')
