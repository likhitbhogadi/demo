import os
from flask import Flask, render_template, request, redirect, session, current_app
# from flask import url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
# from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import create_engine
# from sqlalchemy_cockroachdb import run_transaction
from datetime import datetime
import cv2
import numpy as np
# from moviepy.editor import VideoFileClip
# import requests
from dotenv import load_dotenv
import jwt
import base64
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# load variables from .env into os.environ
load_dotenv()  

# Initialize Flask app
app = Flask(__name__)
app.static_folder = 'static'

# Use environment variables
# app.config is a dictionary-like object in Flask used to store configuration variables.
# app.config['SOME_KEY'] = value assigns a value to a configuration key.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Create engine with environment variable
if os.environ.get('DATABASE_URL'):
    engine = create_engine(os.environ.get('DATABASE_URL'))
else:
    raise ValueError("DATABASE_URL environment variable not set")

# Define User model
# model-1
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

# model-2
class Image(db.Model):
    image_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    image_data = db.Column(db.BLOB, nullable=False)  # This line should match the column in your database

# function-1
def decode_token(token):
    """
    Decode JWT token and return the payload
    """
    try:
        # Decode the JWT token using the app's secret key
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# function-2
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

# function-3
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        user_id = session['user_id']
        user = User.query.get(user_id)
        if not user or user.username != 'admin':
            return redirect('/home')
        return f(*args, **kwargs)
    return decorated_function

# route-1
@app.route('/', methods=['GET', 'POST'])
def landing_and_login_page():

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        user = User.query.filter_by(username=username.lower()).first()

        if user:
            stored_password = user.password
            if check_password_hash(stored_password, password):
                session['user_id'] = user.user_id
                session['username'] = username
                if 'users' not in session:
                    session['users'] = []
                if username not in session['users']:
                    session['users'].append(username)
                return redirect('/home')

        return render_template('landing&loginPage.html', message='Invalid username or password')

    return render_template('landing&loginPage.html')

# route-2
# Route for signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return render_template('signupPage.html', message='Username already exists')

        # Hash the password securely
        hashed_password = generate_password_hash(password)

        try:
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            print(f"Error occurred while querying the database: {str(e)}")
            return render_template('signupPage.html', message='Error occurred while creating user')

        session['user_id'] = new_user.user_id
        session['username'] = username
        return redirect('/')

    return render_template('signupPage.html')

# route-3
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # Get username from session
    username = session.get('username')
    is_admin = False
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    if user:
        is_admin = user.username == 'admin'
        username = user.username
    
    if request.method == 'POST':
        if 'images[]' in request.files:
            images = request.files.getlist('images[]')
            for image in images:
                if image:
                    filename = image.filename
                    image_data = image.read()
                    new_image = Image(user_id=user_id, filename=filename, image_data=image_data)
                    db.session.add(new_image)
                    db.session.commit()
            return redirect('/video')
        else:
            return render_template('homePage.html', message='No images uploaded')
    
    return render_template('homePage.html', tempUser=username, is_admin=is_admin)

#route-4
@app.route('/video', methods=['GET', 'POST'])
@login_required
def video():
    user_id = session['user_id']
    images = Image.query.filter_by(user_id=user_id).all()
    print(f"no.of images: {len(images)}")
    if not images:
        return render_template('videoPage.html', message='No images found')

    # Encode image data to base64 before passing it to the template
    encoded_images = [base64.b64encode(image.image_data).decode('ascii') for image in images]

    # Load the audio clip
    audio_clip = AudioFileClip("static/StarWars60.wav")
    audio_duration = audio_clip.duration
    
    # Check if the audio duration is less than 60 seconds
    if audio_duration < 60:
        # Loop the audio clip until it reaches 60 seconds
        num_loops = int(60 / audio_duration) + 1
        audio_clip = audio_clip.audio_loop(n=num_loops)
    elif audio_duration > 60:
        # Trim the audio clip to 60 seconds
        audio_clip = audio_clip.subclip(0, 60)

    # Create video clip and add audio
    # (Remaining code for creating the video clip goes here...)

    # Determine the selected transition effect
    transition_effect = request.form.get('transitionSelect')
    print(f"Selected transition effect: {transition_effect}")
    # Create video clip with the selected transition effect between images
    clips = []
    total_duration = 0
    for i in range(len(images)):
        image_data = np.frombuffer(images[i].image_data, np.uint8)
        decoded_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        rgb_image = cv2.cvtColor(decoded_image, cv2.COLOR_BGR2RGB)
        height, width, _ = rgb_image.shape
        clip = ImageClip(rgb_image, duration=2).set_position(('center', 'center'))  # Adjust duration as needed

        if transition_effect == "fade-in":
            fadein_duration = 2
            clip = clip.fadein(fadein_duration)
        elif transition_effect == "fade-out":
            fadeout_duration = 2
            clip = clip.fadeout(fadeout_duration)
        elif transition_effect == "crossfade-in":
            crossfade_duration = 2
            clip = clip.crossfadein(crossfade_duration)
        elif transition_effect == "crossfade-out":
            crossfade_duration = 2
            clip = clip.fadeout(crossfade_duration)
        elif transition_effect == "fade-in-fade-out":
            fadein_duration = 1
            fadeout_duration = 1
            clip = clip.fadein(fadein_duration).fadeout(fadeout_duration)
        elif transition_effect == "crossfadeinout":
            crossfade_duration = 2
            clip = clip.fadein(crossfade_duration).fadeout(crossfade_duration)
        elif transition_effect=="null":
            pass

        clips.append(clip)
        total_duration += clip.duration

    # Add a final transition at the end of the video to smoothly end it
    if transition_effect == "fade-out":
        final_transition = clips[-1].fadeout(2)  # Use the same fadeout duration as other transitions
    elif transition_effect == "crossfade-out":
        final_transition = clips[-1].fadeout(2)
    else:
        final_transition = clips[-1].crossfadeout(2)  # Default transition for ending the video

    clips.append(final_transition)

    # Calculate the total duration of the video
    # total_duration = sum(clip.duration for clip in clips)

    # Concatenate all clips to create the final video
    final_clip = concatenate_videoclips(clips, method="compose")
    audio_file_path = request.form.get('selectedAudio')  # Assuming 'selectedAudio' is the name of the audio select field
    if audio_file_path:
        audio_clip = AudioFileClip(audio_file_path)
        final_clip = final_clip.set_audio(audio_clip)

    final_clip = final_clip.set_duration(total_duration)

    # Specify the output video path within the static folder
    static_folder = app.static_folder
    output_video_path = os.path.join(static_folder, "output_video.mp4")

    # Write the video file
    final_clip.write_videofile(output_video_path, codec="libx264", fps=24)
    video_path = 'static/output_video.mp4'

    print(f"Video created successfully at {output_video_path}.")
    return render_template('videoPage.html', images=encoded_images, x=video_path)

#route-5
@app.route('/admin')
@admin_required
def admin():
    user_id = session['user_id']
    user = User.query.get(user_id)
    users = session.get('users', [])
    print("Current users:", users)
    return render_template('adminPage.html', username=user.username, users=users)

# route-6
# Add a logout route to clear session data
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/')

# main function
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Updated for production deployment
    port = int(os.environ.get('PORT', 5038))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')






