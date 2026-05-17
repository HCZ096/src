import flask
import psycopg2
from global_functions import db_connection, logger, StatusCodes



def update_fare(fare_id):

    payload = flask.request.get_json()
    required_fields = ["price",
                    "effective_from"]

    errors = []
    for field in required_fields:
        if field not in payload:
            errors.append(f"Missing {field}")

    if errors:
        return flask.jsonify({
            "status":StatusCodes['api_error'],
            "errors":errors
        })
    conn = db_connection()
    try:


        cur = conn.cursor()


        cur.execute("""UPDATE fare SET price=%s,
                                       duracao=%s,
                                       WHERE id_fare=%s""",
                    (payload["price"],payload["effective_from"],fare_id)
                    )

        if cur.countrow == 0:
            cur.execute("""INSERT INTO fare(preco,duracao)
                           VALUES (%s,%s,%s)""",
                        (payload["price"],payload["effective_from"],fare_id)
                        )


        conn.commit()

    except Exception as error:
        conn.rollback()
        logger.error(f"Error updating price: {error}")

        return flask.jsonify({
            "status": StatusCodes["api_error"],
            "errors": [f"Error updating price: {error}"]
      })

    finally:
        conn.close()