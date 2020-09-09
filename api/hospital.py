from flask import current_app, request, g
from flask_restplus import Namespace, Resource, reqparse, fields
from pymongo.database import Database
from bson.objectid import ObjectId
from bson.errors import InvalidId
import requests
import utils
from datetime import datetime, timedelta
from dateutil.parser import parse

api = Namespace('hospital')

api.model('Hospital', {
    'code': fields.String(attribute='_id'),
    'lat': fields.Float,
    'lng': fields.Float,
    'name': fields.String,
    'number': fields.String
})

api.model('PostReservation', {
    'code': fields.String,
    'time': fields.DateTime
})

api.model('ReservationInfo', {
    'name': fields.String,
    'lat': fields.Float,
    'lng': fields.Float,
    'reservation_id': fields.String,
    'time': fields.DateTime
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

@api.route("/<_id>")
class Info(Resource):
    def get(self, _id):
        db: Database = self.api.db
        try:
            res = db['hospitals'].find_one({'_id': ObjectId(_id)})
        except InvalidId:
            return {'message': utils.ERROR_MESSAGES['invalid_objectid']}, 400
        if not res:
            return {'message': utils.ERROR_MESSAGES['not_exist']}, 404
        return api.marshal(res, api.models['Hospital'])

@api.route("/reservation")
class PostReservation(Resource):
    @api.expect(api.models['PostReservation'])
    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        db: Database = self.api.db
        data = request.json

        try:
            if not db['hospitals'].find_one({'_id': ObjectId(data['code'])}):
                return {'message': utils.ERROR_MESSAGES['not_exist']}, 404
            res = db['hospitalreservations'].insert_one({
                'code': ObjectId(data['code']),
                'who': g.user['_id'],
                'time': parse(data['time']),
                })
            return {'reservation_id': str(res.inserted_id)}
        except KeyError:
            return {'message': utils.ERROR_MESSAGES['bad_request']}, 400
        except InvalidId:
            return {'message': utils.ERROR_MESSAGES['invalid_objectid']}, 400

@api.route("/reservation/list")
class ReservationList(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    @api.param('time')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('time')
        args = parser.parse_args()
        db: Database = self.api.db

        _filter = {'who': g.user['_id']}

        if args['time']:
            date = parse(args['time'])
            date = datetime(date.year, date.month, date.day)
            _filter['time'] = {
                "$gte": date,
                "$lt": date + timedelta(days=1)
            }
        res = db['hospitalreservations'].aggregate([
            {
                "$match": _filter
            },
            {
                "$lookup": {
                    "from": "hospitals",
                    "let": { "_id": "$code" },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": ["$_id", "$$id"]
                                }
                            }
                        }
                    ],
                    "as": "res"
                }
            },
            {
                "$unwind": "$res"
            }
        ])
        lists = []
        for i in res:
            lists.append(api.marshal(i, api.models['ReservationInfo']))
        
        return {'count': len(lists), 'list': lists}

