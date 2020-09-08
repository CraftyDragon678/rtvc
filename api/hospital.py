from flask_restplus import Namespace, Resource, reqparse

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
        return {'category': args['category'], 'lat': args['lat'], 'lng': args['lng']}
