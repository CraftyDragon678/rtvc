from flask import g, request
from flask_restplus import Namespace, Resource, fields
import utils

api = Namespace('users')

@api.route("/me")
class Me(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self):
        return g.user

@api.route("/list")
class UserList(Resource):
    def get(self):
        db: Database = self.api.db
        res = db['users'].find({}, projection={'_id': 1, 'nickname': 1})
        res = list(res)
        return {
            "users": res }

@api.route("/position")
class Position(Resource):
    @utils.auth_required
    def post(self):
        db: Database = self.api.db
        data = request.json
        res = db['users'].update({'_id': g.user['_id']}, {
            '$set': data
        })
        return {'status': 'successful'}
        