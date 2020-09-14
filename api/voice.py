from flask import request, g, send_file
from flask_restplus import Namespace, Resource, fields
from pymongo.database import Database
from datetime import datetime
import numpy as np
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
        tts: TTS = self.api.tts
        db: Database = self.api.db

        res = db['embeds'].find_one({'who': g.user['_id']}, sort=[('createdAt', -1)])
        embed = np.array(res['data'], dtype=np.float32)
        data = request.json

        wav = tts.vocode(embed, data['text'])
        wav.seek(0)
        return send_file(wav, mimetype='audio/wav')

    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        tts: TTS = self.api.tts
        db: Database = self.api.db

        embed = tts.encode(request.files['audio'])
        db['embeds'].insert_one({
            'who': g.user['_id'],
            'data': embed.tolist(),
            'createdAt': datetime.utcnow()
            })
        return {'status': "success"}
