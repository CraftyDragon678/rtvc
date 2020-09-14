from flask import request, g
from flask_restplus import Namespace, Resource, fields
from utils import TTS
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
        tts: TTS = self.api.tts
        tts.synthesize(request.files['audio'])
        pass