# Digital Susu & Group Savings Platform

A modern web application for traditional group savings (Susu) built with Flask, HTML, and TailwindCSS with Supabase authentication.

## Project Overview

This platform digitizes the traditional Susu savings system, allowing users to:

- Create and join savings groups
- Track contributions and payouts
- Manage group memberships
- View savings history and upcoming payments
- Secure authentication with Supabase

## Features

- **Supabase Authentication**: Secure user authentication with email/password and social OAuth support
- **Hybrid Auth System**: JWT token validation with session fallback
- **Dashboard**: View all joined groups
- **Group Management**: Create and manage savings groups
- **Payment Tracking**: Track contributions and payouts
- **Mobile-responsive Design**: Works on all devices

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML with TailwindCSS
- **Templating**: Jinja2
- **Authentication**: Supabase + Flask-Login (hybrid)
- **Database**: SQLAlchemy with Flask-Migrate
- **Forms**: Flask-WTF

## Project Structure

```
Susu_app/
├── app/
│   ├── auth/
│   │   ├── routes.py          # Authentication routes
│   │   ├── forms.py           # Login/registration forms
│   │   └── decorators.py      # Supabase auth decorators
│   ├── supabase_client.py     # Supabase client initialization
│   ├── models.py              # Database models
│   └── config.py              # Configuration settings
├── migrations/                # Database migrations
├── tests/                     # Test files
│   └── test_supabase_auth.py  # Authentication tests
├── env.example               # Environment variables template
└── requirements.txt          # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- Supabase account and project

### Installation

1. Clone the repository or download the files

2. Create and activate a virtual environment (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your Supabase credentials:
   ```bash
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   ```

5. Set up the database
   ```bash
   flask db upgrade
   ```

### Supabase Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Go to Settings > API to get your project URL and keys
3. Add the keys to your `.env` file
4. **Important**: Never expose the `SUPABASE_SERVICE_ROLE_KEY` on the client side

### Running the Application

1. Start the Flask development server
   ```bash
   flask run
   ```

2. Open your browser and navigate to `http://127.0.0.1:5000`

## Authentication System

### How it Works

The app uses a hybrid authentication system:

1. **Supabase Authentication**: Handles user registration, login, and JWT token management
2. **Local User Profiles**: Stores user data in your local database linked via `supabase_id`
3. **Progressive Fallback**: 
   - First tries JWT token validation from Authorization header
   - Falls back to Flask session-based authentication
   - Maintains backward compatibility with existing sessions

### API Endpoints

- `POST /auth/api/signup` - Create new user account
- `POST /auth/api/login` - Authenticate user
- `POST /auth/api/verify-token` - Verify JWT token
- `GET/POST /auth/register` - Web form registration
- `GET/POST /auth/login` - Web form login
- `POST /auth/logout` - Logout user

### Using the Auth Decorator

```python
from app.auth.decorators import supabase_auth_required

@app.route('/protected')
@supabase_auth_required
def protected_route():
    # Access current user via Flask-Login
    return f"Hello {current_user.full_name}!"
```

## Testing

Run the test suite:

```bash
pytest tests/
```

The tests include:
- User model with Supabase ID
- Authentication API endpoints
- Token verification
- Error handling

## Migration Plan

### From Supabase to Self-Hosted Auth

If you want to migrate away from Supabase authentication later:

1. **Keep the `supabase_id` field**: This serves as a unique identifier
2. **Implement your own auth system**: Create your own JWT or session-based auth
3. **Update the decorator**: Modify `@supabase_auth_required` to use your auth system
4. **Migrate user data**: The local user profiles remain unchanged
5. **Update environment variables**: Replace Supabase config with your auth config

### To Another Auth Provider

1. **Map the `supabase_id`**: Use it as a foreign key to your new auth provider's user ID
2. **Update authentication logic**: Modify the auth decorators and routes
3. **Keep local profiles**: Your app data remains intact

## Security Notes

- **Service Role Key**: Never expose `SUPABASE_SERVICE_ROLE_KEY` in client-side code
- **Environment Variables**: Keep your `.env` file secure and never commit it to version control
- **Token Validation**: Always validate JWT tokens server-side
- **HTTPS**: Use HTTPS in production for secure token transmission

## Development Notes

- The app maintains backward compatibility with existing Flask-Login sessions
- Supabase handles password hashing and security
- Local database stores user profiles and app data
- JWT tokens are validated server-side for security

## License

This project is licensed under the MIT License - see the LICENSE file for details.