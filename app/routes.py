from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegForm, LoginForm, UpdateAccForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image

posts = [
    {
        'author': 'Jeevan',
        'title': 'First post',
        'content': 'First post content',
        'date_posted': 'Nov 20, 2019'
    },
    {
        'author': 'Barbara',
        'title': 'Barbs world',
        'content': 'My post content (^_^)',
        'date_posted': 'Nov 15, 2019'
    },
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts = posts)

@app.route("/about")
def about():
    return render_template('about.html', title = 'About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegForm()
    if form.validate_on_submit():
        hashedPwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashedPwd)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            nextPage = request.args.get('next')
            if nextPage:
                return redirect(url_for('account'))    
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful ! Check email and password.','danger')
    return render_template('login.html', title = 'Login', form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def savePicture(formPic):
    randomHex = secrets.token_hex(8)
    _, fext = os.path.splitext(formPic.filename)
    pictureFname = randomHex + fext
    picturePath = os.path.join(app.root_path, 'static/profile_pics', pictureFname)

    output_size = (800, 800)

    i = Image.open(formPic)
    width, height = i.size   # Get dimensions
    new_width = 800
    new_height = 800
    
    left = (width - new_width)/2
    top = (height - new_height)/2
    right = (width + new_width)/2
    bottom = (height + new_height)/2

    # Crop the center of the image
    i = i.crop((left, top, right, bottom))
    i.thumbnail(output_size)

    i.save(picturePath)
    return pictureFname

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccForm()
    if form.validate_on_submit():
        if form.picture.data:
            pictureFile = savePicture(form.picture.data)
            current_user.image = pictureFile
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account information updated.', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username 
        form.email.data = current_user.email  
    imageFile = url_for('static', filename = 'profile_pics/' + current_user.image)
    return render_template('account.html', title = 'Account', imageFile = imageFile, form = form)

# @app.route("/<name>")
# def helloName(name):
#     return "Hey " + name
