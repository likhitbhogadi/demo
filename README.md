# Slideshow Generator Web Application

## Overview
This web application allows users to create custom slideshows by uploading images, selecting transition effects, and adding background music. The application features a secure user authentication system, an intuitive interface for managing uploads, and a powerful video generation engine with various transition options.

## Links
- **GitHub Repository**: [https://github.com/likhitbhogadi/Slideshow-Generator](https://github.com/likhitbhogadi/Slideshow-Generator)
- **Live Demo**: [https://demo-5e8v.onrender.com/](https://demo-5e8v.onrender.com/)

## Features
- **User Authentication System**
    - Secure signup and login functionality
    - Password hashing using Werkzeug security
    - Session management
    - Special admin privileges

- **Image Management**
    - Multiple image upload with drag-and-drop support
    - Image storage in database as binary data
    - User-specific image collections

- **Video Generation**
    - Create videos from uploaded images
    - Adjustable transition durations
    - Various transition effects including:
        - Fade In
        - Fade Out
        - Cross Fade In
        - Cross Fade Out
        - Fade In And Out
        - Cross Fade In And Out
        - No transition

- **Audio Integration**
    - Choose from multiple audio tracks:
        - Cantina Band
        - Baby Elephant Walk
        - Star Wars Theme
    - Audio preview before video generation
    - Automatic audio looping for consistency

- **Video Playback Controls**
    - Play/Pause functionality
    - Rewind capability
    - Download generated videos

- **Admin Panel**
    - View all registered users
    - Special access restrictions
    - User activity monitoring

## Tech Stack
- **Backend**
    - Flask (Python web framework)
    - SQLAlchemy ORM
    - Flask-JWT-Extended for authentication
    - MoviePy for video processing
    - OpenCV for image manipulation

- **Database**
    - CockroachDB (distributed SQL database)
    - PostgreSQL compatibility layer

- **Frontend**
    - HTML5, CSS3
    - JavaScript for interactive elements
    - Custom-designed responsive UI

- **Authentication**
    - JWT (JSON Web Tokens)
    - Werkzeug security for password hashing

- **Development & Deployment**
    - Environment variables via dotenv
    - Render.com deployment configuration

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Environment Setup
1. Clone the repository
     ```bash
     git clone https://github.com/likhitbhogadi/Slideshow-Generator
     cd slideshow-generator
     ```

2. Create a virtual environment
     ```bash
     python -m venv venv
     ```

3. Activate the virtual environment
     - On Windows:
         ```bash
         venv\Scripts\activate
         ```
     - On macOS/Linux:
         ```bash
         source venv/bin/activate
         ```

4. Install dependencies
     ```bash
     pip install -r requirements.txt
     ```

5. Set up environment variables by creating a `.env` file with the following:
     ```
     DATABASE_URL=cockroachdb+psycopg2://<username>:<password>@<host>:26257/defaultdb?sslmode=verify-full&sslrootcert=certs/cc-ca.crt
     FLASK_SECRET_KEY=your-secret-key
     JWT_SECRET_KEY=your-jwt-secret-key
     PORT=5038
     FLASK_DEBUG=True
     ```
     Replace `<username>`, `<password>`, and `<host>` with your CockroachDB credentials.

6. Ensure you have the SSL certificate for CockroachDB in the `certs` directory:
     ```bash
     mkdir -p certs
     # Copy your CockroachDB SSL certificate to certs/cc-ca.crt
     ```

### Running the Application
1. Start the Flask application
     ```bash
     python app.py
     ```

2. Access the application in your browser at:
     ```
     http://localhost:5038
     ```

## Usage Guide

### 1. User Registration and Login
- Visit the homepage and use the login form or navigate to the signup page
- Create an account with a unique username, email, and password
- Login with your credentials

### 2. Uploading Images
- After login, you'll be directed to the home page
- Use the "Upload Images" section to select files or drag and drop images
- Preview audio options available for your slideshow
- Click "Upload" to proceed to the video creation page

### 3. Creating a Slideshow
- Select desired transition effects from the dropdown menu
- Choose background audio for your slideshow
- Select images to include in the slideshow
- Click "Create Video" to generate your slideshow

### 4. Video Preview and Download
- Use the playback controls to preview your slideshow
- Play, pause, and rewind as needed
- Click the "Download Video" button to save the slideshow to your device

### 5. Admin Functions
- Login with admin credentials (username: "admin")
- Access the admin panel to view all registered users
- Monitor user activity on the platform

## Project Structure
- **app.py**: Main application file with routes and core logic
- **templates/**: HTML templates for different pages
    - landing&loginPage.html: Combined landing and login page
    - signupPage.html: User registration page
    - homePage.html: Main interface after login
    - videoPage.html: Video creation and preview interface
    - adminPage.html: Admin control panel
- **static/**: CSS, JavaScript, and media files
    - Audio files for video soundtracks
    - CSS styling files
    - JavaScript functionality
- **certs/**: SSL certificates for database connection
- **.env**: Environment configuration (not tracked in Git)
- **requirements.txt**: Python dependencies
- **render.yaml**: Deployment configuration for Render.com

## Database Schema

### User Table
- user_id (PK): Unique identifier for users
- username: Unique username for login
- email: User's email address
- password: Hashed password string

### Image Table
- image_id (PK): Unique identifier for images
- user_id: Foreign key linking to User table
- filename: Original filename of uploaded image
- image_data: BLOB data containing the binary image

## Future Enhancements
1. **Enhanced Video Editing**
     - Text overlay and captions
     - Custom filters and effects
     - Image editing capabilities within the app

2. **Additional Media Support**
     - Custom audio uploads
     - Video clip integration
     - GIF support and creation

3. **User Experience Improvements**
     - Saved project templates
     - User dashboards with analytics
     - Social media sharing integration

4. **Advanced Features**
     - AI-powered smart transitions
     - Automatic music beat synchronization
     - Theme-based slideshow templates

5. **Performance Optimization**
     - Client-side image compression
     - Async video generation
     - Progressive video loading

## Troubleshooting

### Common Issues
1. **Database Connection Problems**
     - Ensure CockroachDB is running
     - Verify SSL certificate path is correct
     - Check database credentials in .env file

2. **Video Generation Errors**
     - Install necessary codecs for MoviePy
     - Ensure OpenCV is correctly installed
     - Check permissions for writing to static folder

3. **Authentication Issues**
     - Clear browser cookies and cache
     - Reset password if necessary
     - Check JWT configuration in app settings

## Security Considerations
- Passwords are securely hashed using Werkzeug
- Authentication uses JWT tokens
- User sessions are managed securely
- Database connections use SSL encryption

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors
- Project Team: TeamLAB
- Contributors: Likhit, Ansh and Bibek

## Acknowledgments
- Flask community for excellent documentation
- MoviePy and OpenCV libraries for media processing capabilities
- CockroachDB for distributed database functionality
