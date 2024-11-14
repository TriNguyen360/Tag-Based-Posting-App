from py4web import action, request, URL
from .common import db, auth
from .models import parse_post_content, get_user_email
import json

# Main route that serves the index page
@action('index')
@action.uses('index.html', db, auth.user)
def index():
    is_logged_in = 'true' if auth.get_user() else 'false'
    # Provide URLs for frontend API calls and login status
    return dict(
        get_posts_url=URL('get_posts'),
        create_post_url=URL('create_post'),
        delete_post_url=URL('delete_post'),
        is_logged_in=is_logged_in
    )

# Route to fetch all posts
@action('get_posts')
@action.uses(db, auth.user)
def get_posts():
    # Fetch posts ordered by timestamp (newest first)
    posts = db(db.post).select(orderby=~db.post.timestamp).as_list()
    user_email = get_user_email()
    for post in posts:
        # Convert tags from a comma-separated string to a list
        post['tags'] = post['tags'].split(',') if post['tags'] else []
        # Check if the current user can delete the post
        post['can_delete'] = (post['user_email'] == user_email)
        # Format the timestamp for frontend use
        post['timestamp'] = post['timestamp'].isoformat() if post['timestamp'] else None
    return dict(posts=posts)

# Route to create a new post
@action('create_post', method="POST")
@action.uses(db, auth.user)
def create_post():
    user_email = get_user_email()
    content = request.json.get('content', '').strip()
    if not content:
        return dict(error="Post content cannot be empty.")
    tags = parse_post_content(content)
    tags_str = ','.join(tags)
    post_id = db.post.insert(
        user_email=user_email,
        content=content,
        tags=tags_str,
    )
    # Retrieve and prepare the new post data for the response
    post = db.post[post_id].as_dict()
    post['tags'] = tags
    post['can_delete'] = True  # Allow the creator to delete the post
    post['timestamp'] = post['timestamp'].isoformat()
    return dict(post=post)

# Route to delete a post
@action('delete_post', method="POST")
@action.uses(db, auth.user)
def delete_post():
    user_email = get_user_email()
    # Get the post ID from the request
    post_id = int(request.json.get("id"))
    post = db.post[post_id]
    # Only allow deletion if the user is the post's creator
    if post and post.user_email == user_email:
        db(db.post.id == post_id).delete()
        return dict(success=True)
    return dict(success=False)
