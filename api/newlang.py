from flask import request, g
from flask_restplus import Namespace, Resource, fields, reqparse
from pymongo.database import Database
import utils

api = Namespace('newlang')

api.model('PostNewlangAnswer', {
    'answer': fields.Integer
})

@api.route("/")
class Newlang(Resource):
    def get(self):
        db: Database = self.api.db
        res = db['newlangs'].find_one({}, projection={'_id': 0, 'word': 1, 'mean': 1}, sort=[('_id', -1)])
        if res:
            return res
        return {'message': utils.ERROR_MESSAGES['not_exist']}, 404


@api.route("/search")
class SearchNewLang(Resource):
    @api.param("word", type=str)
    def get(self):
        db: Database = self.api.db
        parser = reqparse.RequestParser()
        parser.add_argument('word', type=str)
        args = parser.parse_args()
        res = db['newlangs'].find_one({'word': args['word']}, projection={'_id': 0, 'word': 1, 'mean': 1})
        if res:
            return res
        return {'message': utils.ERROR_MESSAGES['not_exist']}, 404

@api.route("/quiz")
class Quiz(Resource):
    def get(self):
        db: Database = self.api.db
        res = db['newlangs'].find_one({}, projection={'_id': 0, 'quiz.question': 1, 'quiz.choice': 1}, sort=[('_id', -1)])
        if res:
            # quiz = {
            #     'quiz': res['quiz']['question'],
            #     'answer': res['quiz']['answer'],
            #     'description': res['quiz']['description']
            # }
            return res['quiz']
        return {'message': utils.ERROR_MESSAGES['not_exist']}, 404

    @api.expect(api.models['PostNewlangAnswer'])
    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        db: Database = self.api.db
        res = db['newlangs'].find_one({}, projection={'quiz.answer': 1, 'quiz.description': 1}, sort=[('_id', -1)])
        try:
            user = db['users'].find_one({'_id': g.user['_id']})
            # if 'lastquiz' in user and user['lastquiz'] == res['_id']:
            #     return {'message': "already solved"}, 400

            if int(request.json['answer']) == res['quiz']['answer']:
                db['users'].update_one({'_id': g.user['_id']}, {
                    "$inc": {'newlangscore': 1},
                    "$set": {'lastquiz': res['_id']}
                    })
                return {'message': "correct", 'description': res['quiz']['description']}
            return {'message': "wrong", 'description': res['quiz']['description']}
        except ValueError:
            return {'message': utils.ERROR_MESSAGES['bad_request']}, 400
        except KeyError:
            return {'message': utils.ERROR_MESSAGES['bad_request']}, 400


@api.route("/level")
class Level(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self):
        db: Database = self.api.db
        res = db['users'].find_one({'_id': g.user['_id']})
        if 'newlangscore' in res:
            return {'score': res['newlangscore']}
        db['users'].update_one({'_id': g.user['_id']}, {"$set": {'newlangscore': 0}})
        return {'score': 0}