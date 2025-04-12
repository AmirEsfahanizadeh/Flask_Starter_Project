from flask import Blueprint, request, jsonify
from models import User, Post, Comment
from extensions import db
import jwt
import datetime
import os
from functools import wraps

auth_bp = Blueprint('auth', __name__)
post_bp = Blueprint('post', __name__)
comment_bp = Blueprint('comment', __name__)

SECRET_KEY = os.environ.get('SECRET_KEY', 'very-secrettt')

def token_required_decorator(f):
    """
    This decorator checks if the request contains a valid JWT token.
    If the token is valid, it adds the user_id to the request object.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']  
            # print("current_user_id", current_user_id)
            request.current_user_id = current_user_id  
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()


    if user and user.check_password(password):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({'token': token})

    return jsonify({'error': 'Invalid credentials'}), 401

# GET all posts
@post_bp.route('/posts', methods=['GET'], endpoint="get_all_posts")
def get_posts():
    posts = Post.query.all()  
    return jsonify([post.to_dict() for post in posts])

# CREATE a new post
@post_bp.route('/posts', methods=['POST'], endpoint="create_post")
@token_required_decorator
def create_post():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400

    new_post = Post(title=title, content=content, user_id=request.current_user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify(new_post.to_dict()), 201

# UPDATE a post by ID
@post_bp.route('/posts/<int:id>', methods=['PUT'], endpoint="update_post")
@token_required_decorator
def update_post(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if title:
        post.title = title
    if content:
        post.content = content

    db.session.commit()
    return jsonify({f"message': 'Post {id} updated successfully!"})

# DELETE a post by ID
@post_bp.route('/posts/<int:id>', methods=['DELETE'], endpoint="delete_post")
@token_required_decorator
def delete_post(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': f'Post {id} deleted successfully!'}), 200

# GET all posts by a specific user
@post_bp.route('/users/<int:user_id>/posts', methods=['GET'], endpoint="get_posts_by_user")
@token_required_decorator
def get_posts_by_user(user_id):
    posts = Post.query.filter_by(user_id=user_id).all()
    return jsonify([post.to_dict() for post in posts])

# GET a single post by ID
@post_bp.route('/posts/<int:id>', methods=['GET'], endpoint="get_post_by_id")
def get_post(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404 
    return jsonify(post.to_dict())

# Get all comments
@comment_bp.route('/comments', methods=['GET'], endpoint="get_all_comments")
def get_all_comments():
    comments = Comment.query.all()
    return jsonify([comment.to_dict() for comment in comments])

# Get comments for a specific post
@comment_bp.route('/posts/<int:post_id>/comments', methods=['GET'], endpoint="get_comments_for_post")
def get_comments_for_post(post_id):
    comments = Comment.query.filter_by(post_id=post_id).all()
    return jsonify([comment.to_dict() for comment in comments])


# CREATE a comment
@comment_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@token_required_decorator
def create_comment(post_id):
    data = request.get_json()
    content = data.get('content')

    if not content or not post_id:
        return jsonify({'message': 'Content and post ID are required'}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404

    new_comment = Comment(content=content, user_id=request.current_user_id, post_id=post_id)  # Assign user_id from the token
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({'message': 'Comment created successfully!'}), 201

# UPDATE a comment by ID
@comment_bp.route('/comments/<int:id>', methods=['PUT'], endpoint="update_comment")
@token_required_decorator
def update_comment(id):
    comment = Comment.query.get(id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    data = request.get_json()
    content = data.get('content')

    if content:
        comment.content = content

    db.session.commit()
    return jsonify({'message': f'Comment {id} updated successfully!'})

# DELETE a comment by ID
@comment_bp.route('/comments/<int:id>', methods=['DELETE'], endpoint="delete_comment")
@token_required_decorator
def delete_comment(id):
    comment = Comment.query.get(id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': f'Comment {id} deleted successfully!'}), 200
