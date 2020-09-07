from flask_restplus import Namespace, Resource

api = Namespace('hospital')

@api.route("/list")
class List(Resource):
    def get(self):
        pass
