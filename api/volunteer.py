from flask import request, g
from flask_restplus import Namespace, Resource, fields
from pymongo.database import Database
from bson.objectid import ObjectId
from bson.errors import InvalidId
import random
import db
import utils

api = Namespace('volunteer')

api.model('Letter', {
    'from': fields.Integer,
    'to': fields.Integer,
    'from_name': fields.String,
    'title': fields.String(required=True),
    'file': fields.String,
    'message': fields.String
})

api.model('PostLetter', {
    'to': fields.Integer(required=True),
    'title': fields.String(required=True),
    'file': fields.String,
    'message': fields.String
})

api.model('LetterInfo', {
    '_id': fields.String,
    'from': fields.Integer,
    'to': fields.Integer,
    'title': fields.String,
    'from_name': fields.String,
    'file': fields.String,
    'message': fields.String
})

@api.route("/")
class Volunteer(Resource):
    @api.expect(api.models['PostLetter'])
    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        db: Database = self.api.db
        data = request.json

        if not 'to' in data:
            return {"message": utils.ERROR_MESSAGES['no_user'] % "you send this message."}, 400
        
        if not db['users'].find_one({'_id': data['to']}):
            return {"message": utils.ERROR_MESSAGES['user_not_exist']}, 400

        newdata = {
            'from': g.user['_id'],
            'to': data['to'],
            'title': data['title'],
            'from_name': g.user['nickname'],
        }
        if 'file' in data:
            newdata['file'] = data['file']
        if 'message' in data:
            newdata['message'] = data['message']

        db['volunteers'].insert(newdata)
        return {'status': 'success'}

@api.route("/<_id>")
@api.param('_id', 'volunteer letter id')
@api.response(200, 'Success')
@api.response(404, 'Not Found')
class LetterId(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self, _id):
        db: Database = self.api.db
        try:
            _id = ObjectId(_id)
        except InvalidId:
            return {'message': utils.ERROR_MESSAGES['invalid_objectid']}, 400
        res = db['volunteers'].aggregate([
            {
                "$match": {
                    "_id": ObjectId(_id),
                    "$or": [
                        {"from": g.user['_id']},
                        {"to": g.user['_id']},
                    ]
                }
            },
        ])
        try:
            res = next(res)
            if res:
                return api.marshal(res, api.models['Letter'])
        except StopIteration:
            return {'message': utils.ERROR_MESSAGES['not_exist']}, 404


@api.route("/list")
class List(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self):
        db: Database = self.api.db
        letters = db['volunteers'].aggregate([
            {
                "$match": {
                    "$or": [
                        {"from": g.user['_id']},
                        {"to": g.user['_id']},
                    ]
                }
            },
            # {
            #     "$project": {
            #         "from": 1, "to": 1, "title": 1
            #     }
            # }
        ])
        return {
            'status': 'success',
            'letters': api.marshal(list(letters), api.models['LetterInfo'])
        }
