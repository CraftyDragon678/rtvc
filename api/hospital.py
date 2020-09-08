from flask import current_app
from flask_restplus import Namespace, Resource, reqparse
import requests

api = Namespace('hospital')

@api.route("/list")
class List(Resource):
    @api.param('category', "OS 정형외과/DR 피부과/GS 일반외과/MG 내과", enum=['OS', 'DR', 'GS', 'MG'])
    @api.param('lat', "위도", type=float)
    @api.param('lng', "경도", type=float)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('category')
        parser.add_argument('lat', type=float)
        parser.add_argument('lng', type=float)
        args = parser.parse_args()

        res = requests.get(
                "https://dapi.kakao.com/v2/local/geo/coord2address.json?x={}&y={}".format(args['lng'], args['lat']),
                headers={"Authorization": "KakaoAK " + current_app.config['KAKAO_REST_API_KEY']}
            ).json()
        if not res['documents']:
            return {'message': "Can't find address"}, 404
        region = res['documents'][0]['address']

        res = requests.get("http://happycastle.xyz/hospital?city={}&gu={}".format(
            region['region_1depth_name'],
            region['region_2depth_name']
        ))
        if res.status_code == 404:
            return {'message': "Can't find hospital"}, 404
        lists = res.json()

        return {'count': len(lists), 'hospitals': lists}
