from flask import request, g
from flask_restplus import Namespace, Resource, fields
from pymongo.database import Database
from bson.objectid import ObjectId
import random
import db
import utils

api = Namespace('letter')

api.model('Letter', {
    'from': fields.Integer,
    'to': fields.Integer,
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
})

@api.route("/")
class Letter(Resource):
    @api.expect(api.models['PostLetter'])
    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        db: Database = self.api.db
        data = request.json

        if not 'to' in data:
            return {"message": "please specify the user who you send this message."}, 400
        
        if not db['users'].find_one({'_id': data['to']}):
            return {"message": "user doesn't exist"}, 400

        newdata = {
            'from': g.user['_id'],
            'to': data['to'],
            'title': data['title'],
        }
        if 'file' in data:
            newdata['file'] = data['file']
        if 'message' in data:
            newdata['message'] = data['message']

        db['letter'].insert(newdata)
        return {'status': 'success'}

@api.route("/<id>")
@api.param('id', 'letter id')
@api.response(404, 'Not Found')
class LetterId(Resource):
    @api.response(200, 'Success')
    def get(self, id):
        db: Database = self.api.db
        res = db['letter'].find_one({"_id": ObjectId(id)})
        if res:
            return api.marshal(res, api.models['Letter'])
        return {'status': 'fail'}, 404

    @api.response(204, "Success")
    def delete(self, id):
        db: Database = self.api.db
        res = db['letter'].delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return "", 204
        return {'status': 'fail'}, 404

@api.route("/list")
class List(Resource):
    def get(self):
        db: Database = self.api.db
        return {
            'status': 'success',
            'letters': api.marshal(list(db['letter'].find()), api.models['LetterInfo'])
        }
