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

api.model('MedicinePost', {
    'name': fields.String,
    'amount': fields.Integer,
})

api.model('DateMedicine', {
    'morning': fields.List(fields.Nested(api.models['Medicine'])),
    'lunch': fields.List(fields.Nested(api.models['Medicine'])),
    'evening': fields.List(fields.Nested(api.models['Medicine']))
})

api.model('DateMedicinePost', {
    'morning': fields.List(fields.Nested(api.models['MedicinePost'])),
    'lunch': fields.List(fields.Nested(api.models['MedicinePost'])),
    'evening': fields.List(fields.Nested(api.models['MedicinePost']))
})

api.model('TodayMedicine', {
    'medicines': fields.List(fields.Nested(api.models['Medicine'])),
})

api.model('PostMedicine', {
    'from': fields.DateTime,
    'to': fields.DateTime,
    'medicine': fields.Nested(api.models['DateMedicinePost'])
})

api.model('EatMedicine', {
    'time': fields.String
})
@api.route("/<date>")
@api.param("date", "2006-01-02 같은 형태로")
class Medicine(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    @api.marshal_with(api.models['DateMedicine'])
    def get(self, date):
        db: Database = self.api.db
        date = dateutil.parser.parse(date)
        res = db['medicine'].find({
            'start': {'$lte': date},
            'end': {'$gte': date},
            'who': g.user['_id']
        }, projection={'time': 1, 'name': 1, 'amount': 1})
        medicines = {
            'morning': [],
            'lunch': [],
            'evening': []
        }
        for i in res:
            medicines[i['time']].append(i)
        return medicines


@api.route("/")
class PostMedicine(Resource):
    @api.expect(api.models['PostMedicine'])
    @api.doc(security="jwt")
    @utils.auth_required
    def post(self):
        data = request.json
        db: Database = self.api.db
        start = dateutil.parser.parse(data['from'])
        end = dateutil.parser.parse(data['to'])
        medicines = []
        for time in ['morning', 'lunch', 'evening']:
            for item in data['medicine'][time]:
                medicines.append({
                    **item,
                    'start': start,
                    'end': end,
                    'time': time,
                    'who': data['who'],
                    'dates': []
                })
        db['medicine'].insert_many(medicines)
        return {'status': "success"}


@api.route("/now")
class Now(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    @api.marshal_with(api.models['TodayMedicine'])
    def get(self):
        db: Database = self.api.db
        today = datetime.now()
        today2 = datetime.now().strftime('%Y-%m-%d')
        res = db['medicine'].find({
            'start': {'$lte': today},
            'end': {'$gte': today},
            'who': g.user['_id'],
            'dates': {
                '$nin': [
                    today2
                ]
            }
        }, projection={'time': 1, 'name': 1, 'amount': 1})
        return {'medicines': list(res)}

@api.route("/eat")
class Eat(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    @api.marshal_with(api.models['EatMedicine'])
    def post(self):
        db: Database = self.api.db
        data = request.json
        today = datetime.now().strftime('%Y-%m-%d')
        res = db['medicine'].find({
            'who': g.user['_id'],
            'time': data['time']
        })
        if not today in res[0]['dates']:
            db['medicine'].update({
                'who': g.user['_id'],
                'time': data['time']
            }, {
                '$push': {
                    'dates': today
                }
            })
            return {
                'status': 'successful'
            }
        else:
            return {
                'status': 'Already Ate'
            }