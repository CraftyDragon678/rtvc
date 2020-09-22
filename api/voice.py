from flask import request, g, send_file
from flask_restplus import Namespace, Resource, fields
from pymongo.database import Database
from datetime import datetime
import io
import soundfile as sf
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

@api.route("/hello")
@api.response(404, "there is not embed data")
class Hello(Resource):
    @utils.nugu_auth_required
    def get(self):
        db: Database = self.api.db
        res = db['hello'].find_one({'who': g.user['_id']})
        if res:
            wav = res['data']
            file = io.BytesIO()
            sf.write(file, wav, 16000, format='wav')
            return send_file(wav, mimetype='audio/wav')
        return {'message': utils.ERROR_MESSAGES['not_exist']}, 404

@api.route("/care")
@api.response(404, "there is not embed data or didn't set care message")
class Hello(Resource):
    @utils.nugu_auth_required
    def get(self):
        db: Database = self.api.db
        res = db['care'].find_one({'who': g.user['_id']})
        if res:
            wav = res['data']
            file = io.BytesIO()
            sf.write(file, wav, 16000, format='wav')
            return send_file(wav, mimetype='audio/wav')
        return {'message': utils.ERROR_MESSAGES['not_exist']}, 404

    @api.expect(api.models['RequestVoice'])
    @api.doc(security="jwt")
    @utils.auth_required
    def put(self):
        data = request.json

        tts: TTS = self.api.tts
        db: Database = self.api.db
        res = db['embeds'].find_one({'who': g.user['_id']}, sort=[('createdAt', -1)])

        if not res:
            return {'message': utils.ERROR_MESSAGES['not_exist']}, 404
        db['users'].update_one({'_id': g.user['_id']}, {
            "$set": {'care': data['text']}
        })

        # TODO threading, save file
        embed = np.array(res['data'], dtype=np.float32)
        wav = tts.vocode(embed, data['text'])

        return {'status': "success"}
