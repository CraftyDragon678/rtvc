from flask import request, g
from flask_restplus import Namespace, Resource, fields
from pymongo.database import Database
import utils
from datetime import datetime

api = Namespace('medicine')

MEDICINES = [
    {
        "start": datetime(2019, 8, 17),
        "end": datetime(2019, 8, 19),
        "time": "morning",
        "name": "약약",
        "amount": 1
    },
    {
        "start": datetime(2020, 9, 7),
        "end": datetime(2020, 9, 19),
        "time": "morning",
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


    @api.doc(security="jwt")
    @utils.auth_required
    def post(self, date):
        data = request.json
        db: Database = self.api.db
        # db['medicine'].insert_one({

        # })


@api.route("/now")
class Now(Resource):
    @api.doc(security="jwt")
    @utils.auth_required
    def get(self):
        date = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
        print(date)
        medicines = list(filter(lambda x: x['date'] == date, MEDICINES))
        return medicines
