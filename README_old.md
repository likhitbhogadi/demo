# Slideshow Generator Web Application

## Overview
This web application allows users to create custom slideshows by uploading images, selecting transition effects, and adding background music. Users can sign up, log in, upload their images, and generate videos with various visual transitions and audio tracks.

## Features
- **User Authentication**: Secure signup and login functionality
- **Image Upload**: Multiple image upload with drag and drop support
- **Video Generation**: Create videos from uploaded images
- **Transition Effects**: Various transition effects including:
    - Fade In
    - Fade Out
    - Cross Fade In
    - Cross Fade Out
    - Fade In And Out
    - Cross Fade In And Out
    - No transition
- **Audio Selection**: Choose from multiple audio tracks
- **Video Preview**: Preview generated videos before downloading
- **Video Download**: Download the generated slideshow videos
- **Admin Panel**: Special admin access to view registered users

## Tech Stack
- **Backend**: Flask (Python)
- **Database**: CockroachDB with SQLAlchemy ORM
- **Video Processing**: MoviePy, OpenCV
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: JWT (JSON Web Tokens)

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Environment Variables
Set the following environment variables:
```
DATABASE_URL=cockroachdb://username:password@host:port/dbname?sslmode=verify-full
FLASK_SECRET_KEY=your_secret_key
FLASK_DEBUG=True  # Set to False in production
```

### Installation Steps
1. Clone the repository
     ```
     git clone <repository-url>
     cd <repository-directory>
     ```

2. Install dependencies
     ```
     pip install -r requirements.txt
     ```

3. Run the application
     ```
     python app.py
     ```
     The application will be available at http://localhost:5038

## Application Structure
- **templates/**: HTML templates for the application
- **static/**: CSS, JavaScript, and other static files
- **app.py**: Main application file
- **root.crt**: SSL certificate for database connection

## Database Schema
- **User Table**: Stores user information (username, email, password)
- **Image Table**: Stores uploaded images with references to the user who uploaded them

## Usage
1. Register a new account or log in with existing credentials
2. Upload images from the home page
3. Select transition effects and audio for your slideshow
4. Generate and preview your video
5. Download the video or make changes as needed

## Admin Access
The admin user (username: "admin") has access to a special admin panel showing all registered users.

## Security Features
- Password hashing using JWT
- CSRF protection
- Secure session management

## Future Enhancements
- More transition effects and animation options
- Custom audio upload
- Image editing capabilities
- Social sharing features
- User video galleries

## Contributors
- TeamLAB

## License


