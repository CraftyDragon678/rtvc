from pymongo.database import Database
from flask import current_app
from flask_restplus import Namespace, Resource, fields, reqparse
import requests
import jwt
import os, datetime

datetime.datetime.strftime

api = Namespace('auth')

@api.route("/kakao")
class Kakao(Resource):
    @api.param("code", "auth code")
    @api.param("token", "")
    @api.response(200, "Success")
    @api.response(400, "Bad Request (Auth failed)")
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('code')
        parser.add_argument('token')
        args = parser.parse_args()

        access_token = args['token']

        if not access_token:
            res = requests.post("https://kauth.kakao.com/oauth/token", {
                'grant_type': "authorization_code",
                'client_id': os.getenv("KAKAO_CLIENT_ID"),
                'redirect_uri': os.getenv("KAKAO_REDIRECT_URI"),
                'code': args['code'],
                'client_secret': os.getenv("KAKAO_CLIENT_SECRET")
            })
            if res.status_code != 200:
                return {'status': 'fail'}, 400

            access_token = res.json()['access_token']

        db: Database = self.api.db

        res = requests.get("https://kapi.kakao.com/v2/user/me", headers={
            'Authorization': "Bearer " + access_token
        })
        if res.status_code != 200:
            return {'status': 'fail'}, 400

        me = res.json()
        kakao_account = me['kakao_account']

        get_attr = lambda attr: kakao_account[attr] if kakao_account['has_' + attr] and not kakao_account[attr + '_needs_agreement'] else None
        userdata = {
            'type': "KAKAO",
            'connected_at': datetime.datetime.strptime(me['connected_at'], "%Y-%m-%dT%H:%M:%SZ"),
            'nickname': kakao_account['profile']['nickname'],
            'email': get_attr('email'),
            'age_range': get_attr('age_range'),
            'birthday': get_attr('birthday'),
            'gender': get_attr('gender'),
        }
        
        db['users'].update({'_id': me['id']}, userdata, upsert=True)

        userdata['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)
        del userdata['connected_at']

        token = jwt.encode(userdata, current_app.config['JWT_SECRET_KEY'], "HS256")

        return {
            'token': token.decode("UTF-8")
        }
