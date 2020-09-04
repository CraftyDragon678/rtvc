from flask_restplus import Namespace, Resource, fields, reqparse
import requests
import os

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
        if res.status_code == 200:
            data = res.json()
            return {
                'token_type': data['token_type'],
                'access_token': data['access_token'],
                'refresh_token': data['refresh_token'],
                'expires_in': data['expires_in'],
                'refresh_token_expires_in': data['refresh_token_expires_in']
            }
        return {'status': 'fail'}, 400
