from flask_restplus import Namespace, Resource, fields

api = Namespace('test', description='test namespace')

@api.route("/")
class Test(Resource):
    def get(self):
        return "test"
