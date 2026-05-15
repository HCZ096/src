import flask
import logging
import psycopg2
import time
from datetime import datetime, timedelta


from global_functions import db_connection, logger, StatusCodes
import jwt
import bcrypt
from functools import wraps
from flask import jsonify, make_response
from flask_jwt_extended import get_jwt,create_access_token,set_access_cookies

logging.basicConfig(
    filename='log_file.log',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%H:%M:%S'
)

#logger = logging.pg('logger')

app = flask.Flask(__name__)

db = db_connection()

def authenticate_user():

    route_string = 'PUT /dbproj/user'
    logger.info(route_string)

    payload = flask.request.get_json()

    print(payload)

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



    try:

        conn = db_connection()
        cur = conn.cursor()

        username = payload['username']
        pwd = payload['password'].encode('utf-8')

        statement = """
            SELECT user_id, password
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


        role = None

        cur.execute("""
           SELECT 1 FROM cliente
           WHERE cliente_utilizador_user_id = %s
           """, (user_id,))
        if cur.fetchone():
            role = 'cliente'
        else:
            cur.execute("""
               SELECT role FROM adm
               WHERE administrador_utilizador_user_id = %s
               """, (user_id,))
            admin = cur.fetchone()
            if admin:
                role = True if admin[0] else False

        if role is None:
            return jsonify({
                'status': StatusCodes['api_error'],
                'error': "Utilizador sem role"
            })

        password_is_valid = False

        try:
            password_is_valid = bcrypt.checkpw(pwd, real_pwd.encode('utf-8'))
        except ValueError:
            password_is_valid = payload['password'] == real_pwd
            if password_is_valid:
                hashed_password = bcrypt.hashpw(pwd, bcrypt.gensalt()).decode('utf-8')
                cur.execute("""
                    UPDATE utilizador
                    SET password = %s
                    WHERE user_id = %s
                    """, (hashed_password, user_id))
                conn.commit()

        if password_is_valid:

            token_data = create_access_token(
                identity=str(user_id),
                additional_claims={"role": role}
            )


            response = make_response(jsonify({
                "status": StatusCodes['api_success'],
                "token": token_data

            }))
            set_access_cookies(response, token_data)

            return response

        else:
            response = {
                'status': StatusCodes['api_error'],
                'results': 'Password errada'
            }

        conn.commit()

    except Exception as error:
        if conn:
            conn.rollback()

        return jsonify({
            'status': StatusCodes['api_error'],
            'error': str(error)
        })

    finally:
        if cur :
            cur.close()
        if  conn :
            conn.close()


    return response


def role_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            jwt_data = get_jwt()
            user_role = jwt_data.get('role')

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
