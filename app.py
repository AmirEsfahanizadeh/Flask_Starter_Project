from flask import Flask
from extensions import db
from models import User, Post, Comment
from auth import auth_bp, post_bp, comment_bp
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(auth_bp)
app.register_blueprint(post_bp)
app.register_blueprint(comment_bp)
migrate = Migrate(app, db)

with app.app_context():

    comments = db.session.query(Comment).all()

    for comment in comments:
        print(f"comment ID: {comment.id}, user: {comment.user_id}, post: {comment.post_id}")
        user = User.query.filter_by(id=comment.user_id).first()
        print(f"User ID: {user.id}, Username: {user.username}")

        post = Post.query.filter_by(id=comment.post_id).first()
        print(f"Post ID: {post.id}, Title: {post.title}")
        print("post booood" if post else "post not found")

if __name__ == '__main__':
    app.run(debug=True)