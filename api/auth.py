from pymongo.database import Database
from flask_restplus import Namespace, Resource, fields, reqparse
import requests
import os, datetime

datetime.datetime.strftime

api = Namespace('auth')

@api.route("/kakao")
class Kakao(Resource):
    @api.param("code", "auth code")
    @api.response(200, "Success")
    @api.response(400, "Bad Request (Auth failed)")
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('code')
        args = parser.parse_args()

        res = requests.post("https://kauth.kakao.com/oauth/token", {
            'grant_type': "authorization_code",
            'client_id': os.getenv("KAKAO_CLIENT_ID"),
            'redirect_uri': os.getenv("KAKAO_REDIRECT_URI"),
            'code': args['code'],
            'client_secret': os.getenv("KAKAO_CLIENT_SECRET")
        })
        if res.status_code != 200:
            return {'status': 'fail'}, 400

        data = res.json()
        db: Database = self.api.db

        res = requests.get("https://kapi.kakao.com/v2/user/me", headers={
            'Authorization': "Bearer " + data['access_token']
        })
        if res.status_code != 200:
            return {'status': 'fail'}, 400

        me = res.json()
        userdata = {
            'type': "KAKAO",
            'connected_at': datetime.datetime.strptime(me['connected_at'], "%Y-%m-%dT%H:%M:%SZ"),
            'nickname': me['kakao_account']['profile']['nickname']
        }
        
        db['users'].update({'_id': me['id']}, userdata, upsert=True)

        return {
            'token_type': data['token_type'],
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'expires_in': data['expires_in'],
            'refresh_token_expires_in': data['refresh_token_expires_in']
        }
