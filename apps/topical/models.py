"""
This file defines the database models for a simple posting system, including a Post table and utility functions.
"""
import datetime
import re

from .common import db, Field, auth
from pydal.validators import *

def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_user():
    return auth.current_user.get('id') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

db.define_table(
    'post',
    Field('user_email', default=get_user_email),  # Associates post with the user's email
    Field('content', 'text'),  # Main content of the post
    Field('tags', 'string'),  # Comma-separated list of tags
    Field('timestamp', 'datetime', default=get_time),  # Creation timestamp for the post
)

db.commit()

# Utility function to parse tags from post content
def parse_post_content(content):
    """
    Extracts tags from the content of a post.

    Tags are defined as words starting with the '#' symbol.
    The function returns a list of tags without the '#' prefix.

    Example: 'Hello #world' returns ['world']
    """
    return re.findall(r'#(\w+)', content)  # Regular expression to find tags
