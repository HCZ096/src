import flask
import psycopg2
from flask_jwt_extended import get_jwt_identity

from global_functions import db_connection, logger, StatusCodes


def get_lines_next():
    return None
def update_line_operation(line_id):
    payload = flask.request.get_json()
    allowed_line_id=[1,2,3]


    if line_id not in allowed_line_id:
        return flask.jsonify({
            "status":StatusCodes["api_error"],
            "errors":["Invalid fixed line id"]
        })

    required_field=[
        "start_time",
        "end_time",
        "frequency_minutes"]

    errors = []

    for field in required_field:
        if field not in payload:
            errors.append(f"Missing {field}")



    forbidden_field=[
        "origem_linha",
        "destino_linha",
        "tipo_linha",
        "nome_linha",
        "stations"
    ]

    for field in forbidden_field:
        if field in payload:
            errors.append(f"Field cannot be changed.{field}")


    if errors:
        return flask.jsonify({
            "status":StatusCodes["api_error"],
            "errors":errors
        })
    start_time = payload['start_time']
    end_time = payload['end_time']
    frequency_minutes = payload['frequency_minutes']
    vehicle_capacity = payload['vehicle_capacity']

    if frequency_minutes <= 0:
        return errors.append("Frequency minutes must be greater than 0")

    if vehicle_capacity <= 0:
            return errors.append("Vehicle capacity must be greater than 0")

    if errors :
        return flask.jsonify({
            "status":StatusCodes["api_error"],
            "errors":errors
        })

    conn = db_connection()

    try :
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id_linha 
            FROM Linha
            WHERE id_linha = %s
            """,(line_id,)
        )
        if cur.fetchone() is None:
            return flask.jsonify({
                "status":StatusCodes["api_error"],
                "errors":["Invalid linha id"]
            })


        cur.execute(
            """
            UPDATE horario
            SET start_time=%s,
            end_time=%s,
            frequency_minutes=%s
            WHERE id_linha = %s
            """,(start_time,end_time,frequency_minutes,line_id)
        )

        if cur.rowcount == 0:
            cur.execute(
            """
                INSERT INTO horario(
                start_time,
                 end_time,
                 frequency_minutes,
                 id_linha
                )
                VALUES(%s,%s,%s,%s)""",(start_time,end_time,frequency_minutes,line_id)

            )

        cur.execute(
            """
                UPDATE viagem
                SET capacidadev = %s,
                    capacidade_disponivel = %s
                WHERE id_linha = %s
                """,(vehicle_capacity,vehicle_capacity,line_id)
            )

        conn.commit()

        return flask.jsonify({
                "status":StatusCodes["api_success"],
                "errors": []
            })

    except Exception as error:
        conn.rollback()
        logger.error(f"Error updating line: {error}")

        return flask.jsonify({
            "status":StatusCodes["api_error"],
            "errors":[f"Error updating line: {error}"]
        })

    finally:
        conn.close()





