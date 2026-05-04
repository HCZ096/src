import flask
import logging
import psycopg2
import time
from datetime import datetime, timedelta
from global_functions import db_connection, logger, StatusCodes
import jwt
import bcrypt

logging.basicConfig(
    filename='log_file.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger('logger')

app = flask.Flask(__name__)



db = db_connection()


@app.route('/dbproj/user', methods=['PUT'])
def authenticate_user():

    route_string = 'PUT /dbproj/user'
    logger.info(route_string)

    payload = flask.request.get_json()

    if not payload:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'results': 'JSON inválido ou vazio'
        })

    if 'username' not in payload:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'results': 'username required'
        })

    if 'password' not in payload:
        return flask.jsonify({
            'status': StatusCodes['api_error'],
            'results': 'password required'
        })

    conn = db_connection()
    cur = conn.cursor()

    try:
        username = payload['username']
        pwd = payload['password'].encode('utf-8')

        statement = """
            SELECT id, password
            FROM utilizador
            WHERE username = %s OR email = %s
        """

        cur.execute(statement, (username, username))
        user = cur.fetchone()

        if user is None:
            return flask.jsonify({
                'status': StatusCodes['api_error'],
                'results': 'Utilizador não existe'
            })

        user_id = user[0]
        real_pwd = user[1]

        if bcrypt.checkpw(pwd, real_pwd.encode('utf-8')):

            token_data = {
                'user_id': user_id,
                'username': username
            }

            token = jwt.encode(
                token_data,
                'bd2026',
                algorithm='HS256'
            )

            response = {
                'status': StatusCodes['success'],
                'results': 'Login efetuado!',
                'token': token
            }

        else:
            response = {
                'status': StatusCodes['api_error'],
                'results': 'Password errada'
            }

        conn.commit()

    except Exception as error:

        conn.rollback()

        response = {
            'status': StatusCodes['internal_error'],
            'errors': str(error)
        }


    return flask.jsonify(response)





from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def role_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            jwt_data = get_jwt()
            user_role = jwt_data.get("role")

            if user_role not in allowed_roles:
                return jsonify({
                    "status": 403,
                    "error": "Acesso negado: permissões insuficientes"
                }), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, threaded=True, port=5000)