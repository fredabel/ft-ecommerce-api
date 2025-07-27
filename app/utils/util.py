from datetime import datetime, timedelta, timezone
from urllib.request import urlopen
from jose import jwt
import jose
import json
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv
import os
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN") #The same domain used in your Front-end
API_IDENTIFIER = os.environ.get("API_IDENTIFIER") #The same as the audience for your Fron-end 
ALGORITHMS = ["RS256"] #Encoding Algorithm that was set in the API creation.

def encode_token(user_id, role="user"): 
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=1,hours=1), 
        'iat': datetime.now(timezone.utc), 
        'sub': str(user_id),  # User ID
        'role': role # User role
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_IDENTIFIER,
                issuer=f"https://{AUTH0_DOMAIN}/",
            )
            print('PAYLOAD:', payload)
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token is expired.")
        except jwt.JWTClaimsError:
            raise ValueError("Incorrect claims. Check the audience and issuer.")
        except Exception:
            raise ValueError("Unable to parse authentication token.")
    raise ValueError("No matching RSA key.")


def token_required(f):
    @wraps(f) 
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", None)
        if not auth:
            return jsonify({"message": "Authorization header is missing"}), 401

        #Authorization: "Bearer <token>"
        token = auth.split()[1]

        try:
            payload = verify_token(token) #Sending token to be decrypted
        except ValueError as e:
            return jsonify({"message": str(e)}), 401

        request.jwt_payload = payload
        return f(*args, **kwargs)

    return decorated
