# Flask dependancy
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import jsonify
from flask import url_for
from flask import flash
from flask import session as login_session
from flask import make_response
# ORM: SQLAlchemy
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
# OAuth2Client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
# Utility Libraries
import random
import string
import httplib2
import json
import requests
# Model classes
from database_setup import Base
from database_setup import Country
from database_setup import Missile
from database_setup import User

# Creation of app
app = Flask(__name__)

# Read the credentials from the client _secrets file for Google Authentication
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to missiles database
engine = create_engine('sqlite:///lots_of_missiles.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# User Helper Functions


def create_user(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_by_id(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_userid_by_email(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# ||------------------------------------------------||
# || Routes for the login, logout and OAuth.        ||
# || Can be used for all flask based applications   ||
# ||------------------------------------------------||


@app.route('/login')
def login():
    # Protection against Session riding
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    # Store the state in the login session object
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Check for valid state
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps(
            'Invalid state parameter. This could be due to a session riding attack.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Authorization code from Google
    code = request.data

    try:
        # Constuction of a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check for validity of access token
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Error handling
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # User ID verification
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("User ID mismatch."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Client ID Verification
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("App Client ID mistach."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'User active.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    g_response = requests.get(url, params=params)

    data = g_response.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = get_userid_by_email(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('User Inactive.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Delete session variables
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Google logged out.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # Token validity check
        response = make_response(
            json.dumps('Invalid token.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Check for valid state
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps(
            'Invalid state parameter. This could be due to a session riding attack.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Facebook Access Token
    access_token = request.data

    # Read the client secret from the file
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Get user details
    url = "https://graph.facebook.com/v2.4/me"
    # Remove expiry
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    # Save the details to the session object
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Accessing the picture using facebook oauth
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # User ID Check
    user_id = get_userid_by_email(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "Facebook logged out"


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCountries'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCountries'))
# ||------------------------------------------------||
# || End for generic code for the application       ||
# ||------------------------------------------------||


# ||------------------------------------------------||
# || REST Implementation for the application        ||
# ||------------------------------------------------||

@app.route('/country/JSON')
def countriesJSON():
    '''Returns the list of countries in JSON format'''
    countries = session.query(Country).all()
    return jsonify(countries=[i.serialize for i in countries])


@app.route('/country/<int:country_id>/JSON')
def countryMissilesJSON(country_id):
    '''Returns the missiles for a particular country in JSON format'''
    country = session.query(Country).filter_by(id=country_id).one()
    missiles = session.query(Missile).filter_by(country_id=country_id).all()
    return jsonify(missiles=[i.serialize for i in missiles])


@app.route('/country/<int:country_id>/<int:missile_id>/JSON')
def missileJSON(country_id, missile_id):
    '''Returns the missile details for a particular missile in JSON format'''
    missile = session.query(Missile).filter_by(id=missile_id).one()
    return jsonify(missile=missile.serialize)


# ||------------------------------------------------||
# || Main routes for the application                ||
# ||------------------------------------------------||
@app.route('/')
def showCountries():
    missiles = session.query(Missile).order_by(asc(Missile.name))
    countries = session.query(Country).order_by(asc(Country.name))
    if 'username' not in login_session:
        return render_template('public_missiles.html', missiles=missiles, countries=countries)
    else:
        return render_template('private_missiles.html', missiles=missiles, countries=countries)


@app.route('/country/new', methods=['GET', 'POST'])
def newCountry():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCountry = Country(name=request.form['name'],
                             user_id=login_session['user_id'])
        session.add(newCountry)
        flash('Succesfully added %s country' % newCountry.name)
        session.commit()
        return redirect(url_for('showCountries'))
    else:
        return render_template('new-country.html')


@app.route('/country/<int:country_id>/edit/', methods=['GET', 'POST'])
def editCountry(country_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCountry = session.query(Country).filter_by(id=country_id).one()
    if editedCountry.user_id != login_session['user_id']:
        return """<script>(function() {alert("not authorized");})();</script>"""
    if request.method == 'POST':
        if request.form['name']:
            editedCountry.name = request.form['name']
            flash('Country successfully edited %s' % editedCountry.name)
            return redirect(url_for('showCountries'))
    else:
        return render_template('edit-country.html', country=editedCountry)

# Delete a country


@app.route('/country/<int:country_id>/delete/', methods=['GET', 'POST'])
def deleteCountry(country_id):
    if 'username' not in login_session:
        return redirect('/login')
    countryToDelete = session.query(Country).filter_by(id=country_id).one()
    if countryToDelete.user_id != login_session['user_id']:
        return """<script>(function() {alert("not authorized");})();</script>"""
    if request.method == 'POST':
        session.delete(countryToDelete)
        flash('%s successfully deleted' % countryToDelete.name)
        session.commit()
        return redirect(url_for('showCountries', country_id=country_id))
    else:
        return render_template('delete-country.html', country=countryToDelete)

# Show missiles from a country


@app.route('/country/<int:country_id>/')
@app.route('/country/<int:country_id>/missiles/')
def showMissiles(country_id):
    country = session.query(Country).filter_by(id=country_id).one()
    countries = session.query(Country).order_by(asc(Country.name))
    creator = get_user_by_id(country.user_id)
    missiles = session.query(Missile).filter_by(country_id=country_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('public_missiles.html', missiles=missiles,
                               country=country, countries=countries, creator=creator)
    else:
        return render_template('private_missiles.html', missiles=missiles,
                               country=country, countries=countries, creator=creator)

# Create a new missile for a country


@app.route('/country/<int:country_id>/missiles/new/', methods=['GET', 'POST'])
def newMissile(country_id):
    if 'username' not in login_session:
        return redirect('/login')
    country = session.query(Country).filter_by(id=country_id).one()
    if request.method == 'POST':
        newMissile = Missile(name=request.form['name'],
                             country_id=country_id,
                             band_name=request.form['band_name'],
                             country=request.form['country'],
                             youtube_url=request.form['youtube_url'],
                             user_id=login_session['user_id'])
        session.add(newMissile)
        session.commit()
        flash('New missile %s successfully created' % (newMissile.name))
        return redirect(url_for('showMissiles', country_id=country_id))
    else:
        return render_template('new-missile.html', country_id=country_id)

# Edit a missile


@app.route('/country/<int:country_id>/missile/<int:missile_id>/edit', methods=['GET', 'POST'])
def editMissile(country_id, missile_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedMissile = session.query(Missile).filter_by(id=missile_id).one()
    country = session.query(Country).filter_by(id=country_id).one()
    if editedMissile.user_id != login_session['user_id']:
        return """<script>(function() {alert("not authorized");})();</script>"""
    if request.method == 'POST':
        if request.form['name']:
            editedMissile.name = request.form['name']
        if request.form['band_name']:
            editedMissile.band_name = request.form['band_name']
        if request.form['country']:
            editedMissile.country = request.form['country']
        if request.form['youtube_url']:
            editedMissile.youtube_url = request.form['youtube_url']
        session.add(editedMissile)
        session.commit()
        flash('Missile successfully edited')
        return redirect(url_for('showMissiles', country_id=country_id))
    else:
        return render_template('edit-missile.html', country_id=country_id, missile_id=missile_id, item=editedMissile)

# Delete a missile


@app.route('/country/<int:country_id>/missiles/<int:missile_id>/delete', methods=['GET', 'POST'])
def deleteMissile(country_id, missile_id):
    if 'username' not in login_session:
        return redirect('/login')
    country = session.query(Country).filter_by(id=country_id).one()
    missileToDelete = session.query(Missile).filter_by(id=missile_id).one()
    if missileToDelete.user_id != login_session['user_id']:
        return """<script>(function() {alert("not authorized");})();</script>"""
    if request.method == 'POST':
        session.delete(missileToDelete)
        session.commit()
        flash('Missile successfully deleted')
        return redirect(url_for('showMissile', country_id=country_id))
    else:
        return render_template('delete-missile.html', item=missileToDelete)


if __name__ == '__main__':
    app.secret_key = "secret key"
    app.debug = True
    app.run(host='0.0.0.0', port=8080)