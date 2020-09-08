from flask import current_app
from flask_restplus import Namespace, Resource, reqparse, fields
from pymongo.database import Database
from bson.objectid import ObjectId
import requests

api = Namespace('hospital')

api.model('Hospital', {
    'code': fields.String(attribute='_id'),
    'lat': fields.Float,
    'lng': fields.Float,
    'name': fields.String,
    'number': fields.String
})

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

        # ========== 병원 DB가 없어서 직접 구합니다 ==========
        res = requests.get("http://happycastle.xyz/hospital?city={}&gu={}".format(
            region['region_1depth_name'],
            region['region_2depth_name']
        ))
        if res.status_code == 404:
            return {'message': "Can't find hospital"}, 404
        lists = res.json()
        hospitals = []
        db: Database = self.api.db
        for hospital in lists:
            hospital['lat'] = float(hospital['lat'])
            hospital['lng'] = float(hospital['long'])
            del hospital['long']
            db['hospitals'].update_one({'number': hospital['number']}, {"$set": hospital}, upsert=True)
            res = db['hospitals'].find_one({'number': hospital['number']})
            hospitals.append(api.marshal(res, api.models['Hospital']))

        return {'count': len(lists), 'hospitals': hospitals}
