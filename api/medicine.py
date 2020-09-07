from flask import request, g
from flask_restplus import Namespace, Resource, fields
import utils
import datetime

api = Namespace('medicine')

MEDICINES = [
    {
        "date": "2019-08-17",
        "time": "morning",
        "_id": 1,
        "name": "약약",
        "amount": 1
    },
    {
        "date": "2020-09-07",
        "time": "morning",
        "_id": 1,
        "name": "약약",
        "amount": 1
    },
]

@api.route("/<date>")
@api.param("date", "2006-01-02 같은 형태로")
class Medicine(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self, date):
        medicines = list(filter(lambda x: x['date'] == date, MEDICINES))
        return medicines


@api.route("/now")
class Now(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self):
        date = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
        print(date)
        medicines = list(filter(lambda x: x['date'] == date, MEDICINES))
        return medicines
