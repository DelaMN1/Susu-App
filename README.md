# Digital Susu & Group Savings Platform

A modern web application for traditional group savings (Susu) built with Flask, HTML, and TailwindCSS.

## Project Overview

This platform digitizes the traditional Susu savings system, allowing users to:

- Create and join savings groups
- Track contributions and payouts
- Manage group memberships
- View savings history and upcoming payments

## Features

- User authentication (register, login, logout)
- Dashboard to view all joined groups
- Group creation and management
- Payment tracking and notifications
- Mobile-responsive design

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML with TailwindCSS
- **Templating**: Jinja2
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF

## Project Structure

```
Susu_app/
├── app.py                 # Main Flask application
├── static/                # Static assets
│   └── css/
│       └── tailwind.css   # Compiled TailwindCSS
└── templates/             # HTML templates
    ├── base.html          # Base layout template
    ├── index.html         # Landing page
    ├── login.html         # Login page
    ├── register.html      # Registration page
    └── dashboard.html     # User dashboard
```

## Setup Instructions

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone the repository or download the files

2. Create and activate a virtual environment (recommended)
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages
   ```
   pip install flask flask-login flask-wtf email-validator
   ```

4. Set up TailwindCSS (optional - for development)
   ```
   npm install -D tailwindcss
   npx tailwindcss init
   ```
   Configure tailwind.config.js and build the CSS

### Running the Application

1. Start the Flask development server
   ```
   python app.py
   ```

2. Open your browser and navigate to `http://127.0.0.1:5000`

## Development Notes

- This is a template project with mock data
- In a production environment, you would:
  - Connect to a database (SQLAlchemy, PostgreSQL, etc.)
  - Implement proper user authentication and password hashing
  - Add more robust error handling
  - Configure proper deployment settings

## License

This project is licensed under the MIT License - see the LICENSE file for details.