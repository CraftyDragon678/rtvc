from flask import current_app, request, g
from flask_restplus import Namespace, Resource, reqparse, fields
from pymongo.database import Database
from bson.objectid import ObjectId
from bson.errors import InvalidId
import requests
import utils
from datetime import datetime, timedelta
from dateutil.parser import parse

api = Namespace('activity')

api.model('Activity', {
    'code': fields.String(attribute='_id'),
    'category': fields.String,
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
    'category': fields.String,
    'lat': fields.Float,
    'lng': fields.Float,
    'reservation_id': fields.String,
    'time': fields.DateTime
})


api.model('ReservationAdminInfo', {
    'reservation_id': fields.String(attribute='_id'),
    'time': fields.DateTime,
    'who': fields.Nested({
        '_id': fields.Integer,
        'email': fields.String,
        'nickname': fields.String
    })
})

@api.route("/list")
class List(Resource):
    @api.param('category', "EDU 교육/FUN 재미활동/SCL 사교활동", enum=["EDU", "FUN", "SCL"])
    @api.param('lat', "위도", type=float)
    @api.param('lng', "경도", type=float)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('category')
        parser.add_argument('lat', type=float)
        parser.add_argument('lng', type=float)
        args = parser.parse_args()

        activities = []

        return {'count': len(lists), 'activities': activities}


@api.route("/<_id>")
class Info(Resource):
    def get(self, _id):
        db: Database = self.api.db
        try:
            res = db['activities'].find_one({'_id': ObjectId(_id)})
        except InvalidId:
            return {'message': utils.ERROR_MESSAGES['invalid_objectid']}, 400
        if not res:
            return {'message': utils.ERROR_MESSAGES['not_exist']}, 404
        return api.marshal(res, api.models['Activity'])

@api.route("/reservation")
class PostReservation(Resource):
    @api.expect(api.models['PostReservation'])
    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        db: Database = self.api.db
        data = request.json

        try:
            if not db['activities'].find_one({'_id': ObjectId(data['code'])}):
                return {'message': utils.ERROR_MESSAGES['not_exist']}, 404
            res = db['activityreservations'].insert_one({
                    'code': ObjectId(data['code']),
                    'who': g.user['_id'],
                    'time': parse(data['time']),
                    'deleted': False
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
        res = db['activityreservations'].aggregate([
            {
                "$match": _filter
            },
            {
                "$lookup": {
                    "from": "activities",
                    "let": { "id": "$code" },
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
            },
            {
                "$project": {
                    "name": "$res.name",
                    "lat": "$res.lat",
                    "lng": "$res.lng",
                    "category": "$res.category",
                    "reservation_id": "$_id",
                    "time": "$time"
                }
            }
        ])
        lists = []
        for i in res:
            lists.append(api.marshal(i, api.models['ReservationInfo']))
        
        return {'count': len(lists), 'list': lists}


@api.route("/reservation/<_id>")
class DeleteReservation(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def delete(self, _id):
        db: Database = self.api.db

        try:
            res = db['activityreservations'].update_one({
                    '_id': ObjectId(_id),
                    'who': g.user['_id'],
                    'deleted': False
                }, {
                "$set": {
                    'deleted': True
                }
            })

            if res.modified_count:
                return {'status': "success"}
            return {'message': utils.ERROR_MESSAGES['not_exist']}
        except InvalidId:
            return {'message': utils.ERROR_MESSAGES['invalid_objectid']}


@api.route("/reservation/admin/")
class ReservationAdmin(Resource):
    @api.param('code')
    @api.param('time')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('code')
        parser.add_argument('time')
        args = parser.parse_args()

        db: Database = self.api.db

        try:
            _filter = {'code': ObjectId(args['code'])}
            if args['time']:
                date = parse(args['time'])
                date = datetime(date.year, date.month, date.day)
                _filter['time'] = {
                    "$gte": date,
                    "$lt": date + timedelta(days=1)
                }
            res = db['activityreservations'].aggregate([
                {
                    "$match": _filter
                },
                {
                    "$lookup": {
                        "from": "users",
                        "let": { "who": "$who" },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$eq": ["$_id", "$$who"]
                                    }
                                }
                            }
                        ],
                        "as": "who"
                    }
                },
                {
                    "$unwind": "$who"
                }
            ])
            lists = []
            for i in res:
                lists.append(api.marshal(i, api.models['ReservationAdminInfo']))
            
            return {'count': len(lists), 'list': lists}
        except InvalidId:
            return {'message': utils.ERROR_MESSAGES['invalid_objectid']}