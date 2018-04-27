from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from model import User, Rating, Movie, connect_to_db, db
from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension

"""Movie Ratings."""

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    if 'login' in session:
        #condition is not working as expected
        if session['login'] is True:
            return render_template('homepage_signedin.html')
        else:
            return render_template("homepage.html")
    else:
        return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<user_id>')
def display_user_profile(user_id):
    """returns the given user's info"""

    user = User.query.get(user_id)
    user_ratings = user.ratings

    return render_template("user_profile.html", user=user, user_ratings=user_ratings)

@app.route('/register', methods=["GET", 'POST'])
def register_form():

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        age = request.form.get("age")
        zipcode = request.form.get("zipcode")

        #check if in db, else add to db
        if User.query.filter_by(email=email).all():
            flash("User already exists")

        else:
            new_user = User(email=email, password=password, age=age, zipcode=zipcode)

            db.session.add(new_user)
            db.session.commit()
            new_user = User.query.filter_by(email=email).one()

            flash("You have successfully signed up!")
            session['login'] = True
            session['user_id'] = new_user.user_id
            return redirect('/users/{}'.format(session['user_id']))

    return render_template("register_form.html")


@app.route('/check-login.json')
def get_user_login():

    email = request.args.get('email')
    password = request.args.get('password')

    current_user = User.query.filter_by(email=email).all()

    user_validation = {}

    if current_user:
        if current_user[0].password == password:
            session['login'] = True
            session['user_id'] = current_user[0].user_id
            user_validation['valid'] = True
    else:
        user_validation['valid'] = False

    return jsonify(user_validation)


@app.route('/logout')
def log_out():

    session.pop('user_id', None)
    session['login'] = False

    return render_template("homepage.html")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
