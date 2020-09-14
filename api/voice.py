from flask import request, g
from flask_restplus import Namespace, Resource, fields
from utils import TTS
import utils

api = Namespace('voice')

api.model('RequestVoice', {
    'text': fields.List(fields.String)
})

@api.route("/")
class Voice(Resource):
    @api.expect(api.models['RequestVoice'])
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self):
        pass


    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        tts: TTS = self.api.tts
        tts.method(request.files['audio'])
        return {'status': "success"}
