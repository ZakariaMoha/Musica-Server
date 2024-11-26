from functools import wraps
from flask import request, jsonify
import os
import re
# Email validation 
def is_valid_email(email):
    email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    return email_regex.match(email) is not None
# API_KEY function
def verify_api_key(func):
    """
        This decorator function wraps the route function (func) to check for API key in request header
        :param func: Route function 
        :return: decorated function 
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        api_key = None 
        if "X-API-KEY" in request.headers:
            api_key = request.headers["X-API-KEY"]
        if not api_key:
            return jsonify({"message": "Missing API KEY"}), 401
        if api_key  != os.getenv("API_KEY"):
            return jsonify({"message": "Invalid API KEY"}),401
        return func(*args, **kwargs)
    return decorated

# # Token generation function
# def generate_token(expiry, username):
#     """
#        Generate JWT tokens
#        :param expiry: Token expiration
#        :param username: User's username
#        :return: JWT token
#     """
#     token = jwt.encode(
#       {
#         "username": username,
#         "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry)

#       } ,
#       os.environ.get('SECRET_KEY'),
#       algorithm="HS256" 
#     )
#     return token

# def decode_token(token):
#     """
#         Decode JWT token.
#         :param token: JWT token
#         :return Decoded data or None
#     """
#     try: 
#         data = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
#     except jwt.ExpiredSignatureError:
#         return None
#     else:
#         return data
def client_login_required(f):
    """
        Checks whether client is logged in.
        :param f: route function.
        :return: 400, 401, route function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        api_key = None
        if "X-API-KEY" in request.headers:
            api_key = request.headers["X-API-KEY"]

        if not api_key:
            return jsonify({"message": "API KEY is missing"}), 400

        if api_key != os.getenv("API_KEY"):
            return jsonify({"message": "Invalid API KEY"}), 400

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            data = jwt.decode(token, os.getenv('SECRET'), algorithms=["HS256"])
            current_user = Client.query.filter_by(email=data["username"]).first()
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Expired Session! Login Again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid Token. Please Login Again"}), 401
        return f(current_user, *args, **kwargs)
    return decorated


def business_login_required(f):
    """
        Checks whether business/owner is logged in.
        :param f: route function.
        :return: 400, 401, route function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        api_key = None
        if "X-API-KEY" in request.headers:
            api_key = request.headers["X-API-KEY"]

        if not api_key:
            return jsonify({"message": "API KEY is missing"}), 400

        if api_key != os.getenv("API_KEY"):
            return jsonify({"message": "Invalid API KEY"}), 400

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            data = jwt.decode(token, os.getenv('SECRET'), algorithms=["HS256"])
            current_user = Business.query.filter_by(slug=data["username"]).first()
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Expired Session! Login Again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid Token. Please Login Again"}), 401
        return f(current_user, *args, **kwargs)
    return decorated