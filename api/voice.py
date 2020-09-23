from flask import request, g, send_file
from flask_restplus import Namespace, Resource, fields
from pymongo.database import Database
from datetime import datetime
import io, threading, random
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
    @api.response(404, "not ready or didn't request")
    def get(self):
        """
            /voice/play uri 전달
        """
        db: Database = self.api.db
        data = request.json

        embed = db['embeds'].find_one({'who': g.user['_id']}, sort=[('createdAt', -1)])
        res = db['voices'].find_one({'who': g.user['_id'], 'text': data['text']}, sort=[('createdAt', -1)])
        if (not res) or (not embed) or res['createdAt'] < embed['createdAt']:
            return {'message': utils.ERROR_MESSAGES['not_exist']}, 404
        return {'url': f"/voice/play?token={res['token']}"}

    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        """
            원본 목소리를 받아서 embeding시킴
        """
        tts: TTS = self.api.tts
        db: Database = self.api.db

        embed = tts.encode(request.files['audio'])
        db['embeds'].insert_one({
            'who': g.user['_id'],
            'data': embed.tolist(),
            'createdAt': datetime.utcnow()
            })
        return {'status': "success"}

@api.route("/req")
class RequestVoice(Resource):
    @api.expect(api.models['RequestVoice'])
    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        """
            텍스트를 받아서 vocode 시킨 후 파일 전달
        """
        tts: TTS = self.api.tts
        db: Database = self.api.db

        res = db['embeds'].find_one({'who': g.user['_id']}, sort=[('createdAt', -1)])
        embed = np.array(res['data'], dtype=np.float32)
        data = request.json

        wav = tts.vocode(embed, data['text'], True)
        db['voices'].insert_one({
            'token': "%32x" % random.getrandbits(128),
            'who': g.user['_id'],
            'text': data['text'],
            'data': wav.tolist(),
            'createdAt': datetime.utcnow()
        })
        return {'status': "success"}

@api.route("/play")
class PlayVoice(Resource):
    def get(self):
        """
            토큰을 가지고 미리 생성해둔 파일 전달
        """
        db: Database = self.api.db

        token = request.args.get("token")
        res = db['voices'].find_one({'token': token})

        file = io.BytesIO()
        sf.write(file, np.array(res['data']), 16000, format='mp3')
        file.seek(0)
        return send_file(file, mimetype='audio/mp3')

@api.route("/hello")
@api.response(404, "there is not embed data")
class Hello(Resource):
    @utils.nugu_auth_required
    def get(self):
        db: Database = self.api.db
        res = db['hellos'].find_one({'who': g.user['_id']})
        if res:
            wav = res['data']
            file = io.BytesIO()
            sf.write(file, wav, 16000, format='mp3')
            return send_file(wav, mimetype='audio/mp3')
        return {'message': utils.ERROR_MESSAGES['not_exist']}, 404

@api.route("/care")
@api.response(404, "there is not embed data or didn't set care message")
class Hello(Resource):
    @utils.nugu_auth_required
    def get(self):
        db: Database = self.api.db
        res = db['cares'].find_one({'who': g.user['_id']})
        if res:
            wav = res['data']
            file = io.BytesIO()
            sf.write(file, wav, 16000, format='mp3')
            return send_file(wav, mimetype='audio/mp3')
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

        embed = np.array(res['data'], dtype=np.float32)
        wav = tts.vocode(embed, data['text'], True)
        db['cares'].insert_one({
            'who': g.user['_id'],
            'data': wav.tolist(),
            'createdAt': datetime.utcnow()
            })

        return {'status': "success"}
