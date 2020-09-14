from flask import g
from flask_restplus import Namespace, Resource, fields
import utils

api = Namespace('voice')

@api.route("/")
class Voice(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self):
        pass


    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        pass