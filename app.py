from flask import Flask
from extensions import db
from models import User
from auth import auth_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(auth_bp)


# with app.app_context():
#     users = db.session.query(User).all()
#     for user in users:
#         print(f"User name: {user.username}, pass: {user.password_hash}")

# with app.app_context():
#     db.create_all()  # Creates the user table if it doesn't exist

#     # Create a user record
#     user = User(username="manager")
#     user.set_password("manager123")
#     db.session.add(user)
#     db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)