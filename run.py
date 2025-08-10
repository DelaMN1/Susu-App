import os
from app import create_app
from app.extensions import db
from app.models import User, Group, Membership, Transaction

# Create app instance
app = create_app(os.getenv('FLASK_ENV', 'development'))


# Shell context processor
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Group': Group,
        'Membership': Membership,
        'Transaction': Transaction
    }


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)