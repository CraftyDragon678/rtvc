from flask import request, g, send_from_directory
from flask_restplus import Namespace, Resource, fields
from werkzeug import secure_filename
from pymongo.database import Database
from bson.objectid import ObjectId
from bson.errors import InvalidId
import random
import db
import utils

api = Namespace('letter')

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
    'from_name': fields.String,
    'title': fields.String,
    'file': fields.String,
    'message': fields.String
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
            return {"message": utils.ERROR_MESSAGES['no_user'] % "you send this message."}, 400
        
        if not db['users'].find_one({'_id': data['to']}):
            return {"message": utils.ERROR_MESSAGES['user_not_exist']}, 400

        newdata = {
            'from': g.user['_id'],
            'to': data['to'],
            'from_name': g.user['nickname'],
            'title': data['title'],
            'deleted_from': False,
            'deleted_to': False
        }
        if 'file' in data:
            newdata['file'] = data['file']
        if 'message' in data:
            newdata['message'] = data['message']

        db['letters'].insert(newdata)
        return {'status': 'success'}

@api.route("/<_id>")
@api.param('_id', 'letter id')
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
        res = db['letters'].aggregate([
            {
                "$match": {
                    "_id": ObjectId(_id),
                    "$or": [
                        {"from": g.user['_id'], "deleted_from": False},
                        {"to": g.user['_id'], "deleted_to": False},
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

    @api.doc(security="jwt")
    @utils.auth_required
    def delete(self, _id):
        db: Database = self.api.db
        res1 = db['letters'].update_one({"_id": ObjectId(_id), "from": g.user['_id']}, {"$set": {"deleted_from": True}})
        res2 = db['letters'].update_one({"_id": ObjectId(_id), "to": g.user['_id']}, {"$set": {"deleted_to": True}})
        if res1.modified_count or res2.modified_count:
            return {'status': 'success'}
        return {'status': 'fail'}, 404

@api.route("/list")
class List(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self):
        db: Database = self.api.db
        letters = db['letters'].aggregate([
            {
                "$match": {
                    "$or": [
                        {"from": g.user['_id'], "deleted_from": False},
                        {"to": g.user['_id'], "deleted_to": False},
                    ]
                }
            }
            # ,
            # {
            #     "$project": {
            #         "from": 1, "to": 1, "title": 1, "from_name": 1
            #     }
            # }
        ])
        return {
            'status': 'success',
            'letters': api.marshal(list(letters), api.models['LetterInfo'])
        }

@api.route("/file")
class List(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        audio = request.files['audio']
        filename = audio.filename
        ext = filename.split(".")[-1]
        filename = "%32x" % random.getrandbits(128) + "." + ext
        audio.save("files/" + secure_filename(filename))
        return {'status': "success", 'filename': filename}

@api.route("/file/<path:path>")
class StaticFile(Resource):
    def get(self, path):
        return send_from_directory(self.api.app.static_folder, path, as_attachment=True)