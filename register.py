import flask
import psycopg2

from global_functions import db_connection,logger, StatusCodes


def insert_service_user(cur,username,email,password,nif,phone):
    cur.execute("""INSERT INTO utilizador (username,email,passowrd,nif,phone) 
                 VALUES (%s,%s,%s,%s,%s)
                 RETURNING user_id;
                 """,(username,email,password,nif,phone))

    user_id = cur.fetchone()[0]
    return user_id


def insert_cliente(cur,user_id,role_cliente):
    cur.execute("""INSERT INTO cliente (cliente_utilizador_user_id) 
                 VALUES (%s);
                 """,(str(user_id),str(role_cliente)))


def insert_admin(cur,user_id,role_admin):
    cur.execute("""INSERT INTO Admin (administrador_utilizador_user_id) 
                 VALUES (%s);
                 """,(str(user_id),bool(role_admin)))


def register_service_user(user_type):
    commit_state = False

    payload = flask.request.get_json()
    #TRATAR ERROS

    conn = db_connection()
    cur = conn.cursor()


    try:
        cur.execute('BEGIN;')



        user_id = insert_service_user(cur,payload['username'],payload['email'],payload['password'],payload['nif'],payload['phone'])


        if(user_type=='cliente'):
            insert_cliente(cur,user_id,payload['role_cliente'])
        else:
            insert_admin(cur,user_id,payload['role_admin'])#?????



            cur.execute('COMMIT;')
            commit_state = True

            response ={
                'status' : StatusCodes['success'],
                'error' : None,
                'results' :f'user_id {user_id}'
            }


    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        response ={
            'status' : StatusCodes['error'],
            'error' : str(error)
        }

    finally:
        if(commit_state == False):
            cur.execute('ROLLBACK;')
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

    return response



def register_costumer():
        return register_service_user('cliente')


def register_admin():
        return register_service_user('admin')

