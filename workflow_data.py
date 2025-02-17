import datetime

import jwt
from flask_cors import cross_origin
from flask_restful import Resource
from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, distinct, or_
from jwtData import token_required
from models import User, UserGroups, CustomerMaster, db, Workflow
from flask_jwt_extended import jwt_required, get_jwt_identity

JWT_SECRET_KEY = "mysecretkey12345"

class Data_Workflow(Resource):
    @cross_origin()
    @token_required
    def get(self):
        try:
            token = request.headers.get('Authorization')
            jwtData = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            customer_id = jwtData['customerid']

            # groups = (
            #     db.session.query(distinct(UserGroups.user_group))
            #     .filter(or_(UserGroups.customer_id == customer_id, UserGroups.customer_id == 1))
            #     .all()
            # )

            if customer_id != 1:
                groups_self = db.session.query(distinct(UserGroups.user_group)).filter_by(customer_id=customer_id).all()
                group_names_self = [group[0] for group in groups_self]

                groups_infosec = db.session.query(distinct(UserGroups.user_group)).filter_by(customer_id=1).all()
                group_names_infosec = [group[0] for group in groups_infosec]

                all_workflows = []

                print("self groups: ", group_names_self)
                print("infosec groups: ", group_names_infosec)

                records = Workflow.query.filter_by(customer_id=customer_id).all()
                if not records:
                    return jsonify({'message': 'Workflow is empty', 'Self': group_names_self, 'Protean Infosec': group_names_infosec}), 404

                for record in records:
                    print(f"customer id is {record.customer_id} and group is {record.user_group_name}")

                    workflow_details = {
                        'srno': record.id,
                        'order': record.order,
                        'group': record.user_group_name,
                        'main_customer': record.parent_customer_id,
                        'can_initiate': record.initiator_group,
                        'can_pick': record.can_pickup,
                        'can_close': record.can_close,
                        'can_transfer': record.can_transfer
                    }

                    all_workflows.append(workflow_details)

                return jsonify({'message': 'successful', 'workflow': all_workflows, 'Self': group_names_self, 'Protean Infosec': group_names_infosec}), 201

            else:
                # groups_self = db.session.query(distinct(UserGroups.user_group)).filter_by(customer_id=customer_id).all()
                # group_names_self = [group[0] for group in groups_self]

                groups_infosec = db.session.query(distinct(UserGroups.user_group)).filter_by(customer_id=1).all()
                group_names_infosec = [group[0] for group in groups_infosec]

                all_workflows = []

                # print("self groups: ", group_names_self)
                print("infosec groups: ", group_names_infosec)

                records = Workflow.query.filter_by(customer_id=customer_id).all()
                if not records:
                    return jsonify({'message': 'Workflow is empty', 'Self': [],
                                    'Protean Infosec': group_names_infosec}), 404

                for record in records:
                    print(f"customer id is {record.customer_id} and group is {record.user_group_name}")

                    workflow_details = {
                        'srno': record.id,
                        'order': record.order,
                        'group': record.user_group_name,
                        'main_customer': record.parent_customer_id,
                        'can_initiate': record.initiator_group,
                        'can_pick': record.can_pickup,
                        'can_close': record.can_close,
                        'can_transfer': record.can_transfer
                    }

                    all_workflows.append(workflow_details)

                return jsonify({'message': 'successful', 'workflow': all_workflows, 'Self': [],
                                'Protean Infosec': group_names_infosec}), 201

        except Exception as e:
            print("Exception --> ", e)
            return jsonify({'msg': 'Error displaying workflow', 'error': str(e)})