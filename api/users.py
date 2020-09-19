from flask import g
from flask_restplus import Namespace, Resource, fields
import utils

api = Namespace('users')

@api.route("/me")
class Me(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self):
        return g.user
