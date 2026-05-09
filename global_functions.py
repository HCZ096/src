import logging
import psycopg2


"""
    Global variables
"""

db_connection = None
logger = logging.getLogger('logger')
StatusCodes = {
    'api_error': 400,
    'success': 200,
    'internal_error': 500
}



"""
    Global functions
"""

# Connect to the database
def db_connection():
    try:
        db = psycopg2.connect(
            user = 'aulaspl',
            password = 'aulaspl',
            host = 'localhost',
            port = '5433',
            database = 'dbfichas'
        )
        return db
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'Error connecting to the database: {error}')
        return None


# Landing page
def landing_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                background-color: #f2f2f2;
                font-family: Arial, sans-serif;
            }
            .container {
                width: 80%;
                margin: auto;
                text-align: center;
            }
            h1 {
                color: #333;
            }
            p {
                font-size: 1.2em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to the METRO BUS System</h1>
        </div>
    </body>
    </html>
    """

    