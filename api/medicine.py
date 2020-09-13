from flask import request, g
from flask_restplus import Namespace, Resource, fields
from pymongo.database import Database
import utils
from datetime import datetime
import dateutil

api = Namespace('medicine')

api.model('Medicine', {
    '_id': fields.String,
    'name': fields.String,
    'amount': fields.Integer,
    'time': fields.String
})

api.model('TodayMedicine', {
    'medicines': fields.List(fields.Nested(api.models['Medicine'])),
})

@api.route("/<date>")
@api.param("date", "2006-01-02 같은 형태로")
class Medicine(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self, date):
        medicines = list(filter(lambda x: x['date'] == date, MEDICINES))
        return medicines


    @api.doc(security="jwt")
    @utils.auth_required
    def post(self, date):
        data = request.json
        db: Database = self.api.db
        data['from']
        db['medicine'].insert_one({
            
        })


@api.route("/now")
class Now(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    @api.marshal_with(api.models['TodayMedicine'])
    def get(self):
        db: Database = self.api.db
        today = datetime.now()
        res = db['medicine'].find({
            'start': {'$lte': today},
            'end': {'$gte': today},
            'who': g.user['_id']
        }, projection={'time': 1, 'name': 1, 'amount': 1})
        return {'medicines': list(res)}
