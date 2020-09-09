from flask import request, g
from flask_restplus import Namespace, Resource, fields
from pymongo.database import Database
import utils

api = Namespace('advise')

api.model('PostAdvise', {
    'to': fields.Integer,
    'code': fields.String,
    'message': fields.String,
    'todos': fields.List(fields.Nested(api.model('Todo', {
        'name': fields.String
    })))
})

@api.route("/")
class PostAdvise(Resource):
    @api.expect(api.models['PostAdvise'])
    def post(self):
        data = request.json
        db: Database = self.api.db

        try:
            todos = []
            for i in data['todos']:
                todos.append(i['name'])

            db['advices'].insert_one({
                    'to': data['to'],
                    'code': data['code'],
                    'message': data['message'],
                    'todos': todos
                })

            return {'status': "success"}
        except KeyError:
            return {'message', utils.ERROR_MESSAGES['bad_request']}, 400
        except TypeError:
            return {'message', utils.ERROR_MESSAGES['bad_request']}, 400
    
    def get(self):
        pass
