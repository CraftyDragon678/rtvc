from flask import request
from flask_restplus import Namespace, Resource, fields
import random

api = Namespace('letter')

api.model('AccountInfo', {
    'email': fields.String(required=True, attribute='email'),
    'name': fields.String(required=True, attribute='name')
})

api.model('Letter', {
    'from': fields.Nested(api.models['AccountInfo']),
    'to': fields.Nested(api.models['AccountInfo']),
    'name': fields.String(required=True),
    'file': fields.String,
    'message': fields.String
})

api.inherit('PostLetter', api.models['Letter'], {
    'version': fields.String(required=True),
})

api.model('LetterInfo', {
    'id': fields.String,
    'from': fields.Nested(api.models['AccountInfo']),
    'to': fields.Nested(api.models['AccountInfo']),
    'name': fields.String,
})

LETTERS = [

]

@api.route("/")
class Letter(Resource):
    @api.expect(api.models['PostLetter'])
    def post(self):
        letter = request.json
        letter['id'] = '%x' % random.randint(0, 16**32 - 1)
        LETTERS.append(letter)
        return {'status': 'success'}

@api.route("/<id>")
@api.param('id', 'letter id')
@api.response(404, 'Not Found')
class LetterId(Resource):
    def get(self, id):
        letter = list(filter(lambda x: x['id'] == id, LETTERS))
        if len(letter) == 0:
            return {'status': 'fail'}, 404
        return letter[0]

    def delete(self, id):
        pass

@api.route("/list")
class List(Resource):
    def get(self):
        return {
            'status': 'success',
            'letters': api.marshal(LETTERS, api.models['LetterInfo'])
        }
