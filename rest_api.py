
import argparse
import flask
from flask import request,jsonify
import logging
from flask_jwt_extended import jwt_required,JWTManager

from config import Config
from global_functions import landing_page
from authentication import authenticate_user,role_required
from report import demand_periods, top_spenders,monthly_report
from Ticket import validate_ticket
from purchase import purchase_ticket
from promotions import create_promotion
from notices import notice_broadcast
from fare import update_fare
from line_operations import update_line_operation,get_lines_next
from Wallet import wallet_topup
from register import register_admin,register_costumer,register_Sadmin


app = flask.Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)



app.route('/') (landing_page)

# 1. User Authentication
@app.route('/dbproj/user', methods=['PUT'])
def authenticate_user_endpoint():
    return authenticate_user()

## Super Admin functionalities
#2. Add	Administrator
@app.route('/dbproj/register/admin',methods=['PUT'])
@jwt_required()#Comentar
@role_required(True,False)#Comentar para registar o primeiro Sadmin
def register_admin_endpoint():
    payload = request.get_json(silent=True) or {}
    if payload.get('role') is True:
        return register_Sadmin()
    else :
        return register_admin()

#3 Add Customer
@app.route('/dbproj/register/costumer', methods=['POST'])
@jwt_required()
def register_costumer_endpoint():
    return register_costumer()

# 4. update line
@app.route('/dbproj/line_operation/<int:line_id>', methods=['PUT'])
@jwt_required()
@role_required(True,False)
def update_line_operation_endpoint(line_id):
    return update_line_operation(line_id)

# 5.Update fare price
@app.route('/dbproj/fares/<int:fare_id>',methods=['PUT'])
@jwt_required()
@role_required(True,False)
def  update_fare_endpoint(fare_id):
    return update_fare(fare_id)

# 6.Broadcast notice.
@app.route('/dbproj/notices/broadcast', methods=['POST'])
@jwt_required()
@role_required('superadmin', 'admin')
def notice_broadcast_endpoint():
    return notice_broadcast()

#7. Create	promotion/discount	rule
@app.route('/dbproj/promotions', methods=['POST'])
@jwt_required()
@role_required('superadmin', 'admin')
def create_promotion_endpoint():
    return create_promotion()

# Customers functionalities
#8.
@app.route('/dbproj/lines_next', methods=['GET'])
@jwt_required()
@role_required('costumer')
def get_lines_next_endpoint():
    return get_lines_next()
    
#9
@app.route('/dbproj/wallet', methods=['POST'])
@app.route('/dbproj/wallet/topup', methods=['POST'])
@jwt_required()
@role_required('costumer')
def wallet_topup_endpoint():
    return wallet_topup()

# 10.
@app.route('/dbproj/purchase', methods=['POST'])
@jwt_required()
@role_required('costumer')
def purchase_endpoint():
    return purchase_ticket()

# 11.
@app.route('/dbproj/ticket/use/<int:ticket_id>', methods=['POST'])
@jwt_required()
@role_required('costumer')
def validate_ticket_endpoint(ticket_id):
    return validate_ticket(ticket_id)

#Analytics functionalities (Administrators
# 12 . Peak	and	Low	demand	periods

@app.route('/dbproj/report/demand', methods=['GET'])
@jwt_required()
@role_required('admin')
def demand_periods_endpoint():
    return demand_periods()

# 13.top spenders by line
@app.route('/dbproj/report/top_spenders', methods=['GET'])
@jwt_required()
@role_required('admin')
def top_spenders_endpoint():
    return top_spenders()


# 14 .Generate	a	monthly	report
@app.route('/dbproj/report/monthly', methods=['GET'])
@jwt_required()
@role_required('admin')
def monthly_report_endpoint():
    return monthly_report()



if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s]: %(message)s',
        '%H:%M:%S'
    )

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    host = '127.0.0.1'
    port = 8080

    logger.info(f'Server running on http://{host}:{port}')
    app.run(host=host, port=port, threaded=True)
