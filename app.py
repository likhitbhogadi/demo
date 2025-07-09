import os
from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy import create_engine
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import base64
import cv2
from PIL import Image

# Load .env
load_dotenv()

app = Flask(__name__)
app.static_folder = 'static'

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

# Init DB + JWT
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Create engine (extra)
engine = create_engine(os.environ.get('DATABASE_URL'))

# Models
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

class Image(db.Model):
    image_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)

# Decorators
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = User.query.get(session.get('user_id'))
        if not user or user.username != 'admin':
            return redirect('/home')
        return f(*args, **kwargs)
    return wrapper

# Utility function
def optimize_image(file_path, max_width=800, quality=75):
    """Resize and compress image to reduce file size and memory usage"""
    try:
        with Image.open(file_path) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            width, height = img.size
            if width > max_width:
                ratio = max_width / width
                new_height = int(height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            img.save(file_path, 'JPEG', quality=quality, optimize=True)
            
    except Exception as e:
        print(f"Error optimizing image: {e}")

# Routes
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['username'] = username
            session.setdefault('users', []).append(username)
            return redirect('/home')
        return render_template('landing&loginPage.html', message='Invalid username or password')
    return render_template('landing&loginPage.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            return render_template('signupPage.html', message='Username already exists')
        try:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            print(f"Error: {e}")
            return render_template('signupPage.html', message='DB error')
        session['user_id'] = new_user.user_id
        session['username'] = username
        return redirect('/')
    return render_template('signupPage.html')

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    user_id = session['user_id']
    user = User.query.get(user_id)
    is_admin = user.username == 'admin'

    if request.method == 'POST':
        if 'images[]' in request.files:
            files = request.files.getlist('images[]')
            folder = os.path.join('uploads', str(user_id))
            os.makedirs(folder, exist_ok=True)
            for f in files:
                if f:
                    path = os.path.join(folder, f.filename)
                    f.save(path)
                    optimize_image(path, max_width=800, quality=75)  # Optimize image after saving
                    db.session.add(Image(user_id=user_id, filename=f.filename, file_path=path))
            db.session.commit()
            return redirect('/video')
        return render_template('homePage.html', tempUser=user.username, is_admin=is_admin, message='No images uploaded')
    return render_template('homePage.html', tempUser=user.username, is_admin=is_admin)



@app.route('/video', methods=['GET', 'POST'])
@login_required
def video():
    user_id = session['user_id'] # Get user ID from session
    images = Image.query.filter_by(user_id=user_id).all() # Fetch images for this user
    
    if not images:
        return render_template('videoPage.html', images=[], video_url=None) # No images uploaded

    # Encode images for display
    encoded_images = []
    for img in images:
        try:
            with open(img.file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode('ascii') # Encode image to base64
                encoded_images.append(encoded) 
        except Exception as e:
            print(f"Error reading image {img.file_path}: {e}")
            encoded_images.append("")  # Still keep placeholder

    # On GET — show page only
    if request.method == 'GET':
        return render_template('videoPage.html', images=encoded_images, video_url=None)

    # On POST — process form submission
    selected_indices = request.form.getlist('selectedImages')
    print("Selected image indices:", selected_indices)

    if not selected_indices:
        return render_template('videoPage.html', images=encoded_images, video_url=None, message="No images selected.")

    selected_indices = [int(i) for i in selected_indices if i.isdigit()]
    selected_images = [images[i] for i in selected_indices if i < len(images)]

    if not selected_images:
        return render_template('videoPage.html', images=encoded_images, video_url=None, message="No valid images selected.")

    transition = request.form.get('transitionSelect')
    audio_path = request.form.get('selectedAudio')

    print(f"Creating video with transition: {transition}, audio: {audio_path}")

    # Load audio
    try:
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        if audio_duration < 60:
            audio_clip = audio_clip.audio_loop(n=int(60/audio_duration)+1)
        else:
            audio_clip = audio_clip.subclip(0, 60)
    except Exception as e:
        print("Error loading audio:", e)
        audio_clip = None

    clips = []
    for img in selected_images:
        frame = cv2.imread(img.file_path) # Read image using OpenCV
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert to RGB
        clip = ImageClip(rgb, duration=2) # Create ImageClip with 2 seconds duration
        if transition == "fade-in":
            clip = clip.fadein(2)
        elif transition == "fade-out":
            clip = clip.fadeout(2)
        elif transition == "crossfade-in":
            clip = clip.crossfadein(2)
        elif transition == "crossfade-out":
            clip = clip.fadeout(2)
        elif transition == "fade-in-fade-out":
            clip = clip.fadein(1).fadeout(1)
        elif transition == "crossfadeinout":
            clip = clip.fadein(2).fadeout(2)
        # If "null" or anything else: no transition
        clips.append(clip)

    final_clip = concatenate_videoclips(clips, method="compose")
    # Fix: Trim audio to match video duration
    if audio_clip:
        video_duration = final_clip.duration
        if audio_clip.duration > video_duration:
            audio_clip = audio_clip.subclip(0, video_duration)
        final_clip = final_clip.set_audio(audio_clip)

    # Save video
    output_path = f"/tmp/output_{user_id}.mp4"
    final_clip.write_videofile(output_path, codec="libx264", fps=24)
    print(f"Video created at: {output_path}")

    video_url = f"/video/{user_id}"
    return render_template('videoPage.html', images=encoded_images, video_url=video_url)

@app.route('/video/<int:user_id>')
@login_required
def serve_video(user_id):
    return send_from_directory('/tmp', f"output_{user_id}.mp4")

@app.route('/uploads/<int:user_id>/<filename>')
@login_required
def uploaded_file(user_id, filename):
    return send_from_directory(os.path.join('uploads', str(user_id)), filename)

@app.route('/admin')
@admin_required
def admin():
    return render_template('adminPage.html', username=session.get('username'), users=session.get('users', []))

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/')

# Create tables + run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5038))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')
