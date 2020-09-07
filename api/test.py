from flask import g
from flask_restplus import Namespace, Resource, fields
import utils

api = Namespace('test', description='test namespace')

@api.route("/")
class Test(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self):
        return g.user['nickname']