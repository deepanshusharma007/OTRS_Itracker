from flask import jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource, reqparse
from sqlalchemy import exc

from jwtData import token_required
from models import User, UserGroups, db


class DeleteUserFromGroup(Resource):
    @cross_origin()
    @token_required
    def post(self):
        try:
            data = request.get_json()
            group_name = data.get('group_name')
            username = data.get('username')

            if not group_name or not username:
                return jsonify({'error': 'Please provide group name and username'}), 400

            # Find the user ID based on the username
            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Find the user-group relationship
            user_group = UserGroups.query.filter_by(user_id=user.user_id, user_group=group_name).first()
            if not user_group:
                return jsonify({'error': 'User is not a member of the specified group'}), 400

            # Delete the user from the group
            db.session.delete(user_group)
            db.session.commit()

            return jsonify({'message': 'User removed from group successfully'}), 200

        except exc.SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error deleting user from group: {e}")
            return jsonify({'error': 'Error deleting user from group', 'message': str(e)}), 500