from flask import Flask
from flask_restplus import Api
from .medicine import api as medicineNS
from .hospital import api as hospitalNS
from .activity import api as activityNS
from .letter import api as letterNS
from .volunteer import api as volunteerNS
from .advise import api as adviseNS
from .newlang import api as newlangNS
from .voice import api as voiceNS
from .auth import api as authNS
from .users import api as usersNS
from utils import TTS
import db
import os

class AgayaApi(Flask):
    def __init__(self):
        super().__init__(__name__, static_folder='files')
        self.config.SWAGGER_UI_DOC_EXPANSION = 'list'

        self.api = Api(self, title="Agaya API", version='0.2', authorizations={
            'jwt': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization'
            }
        })
        self.api.add_namespace(medicineNS)
        self.api.add_namespace(hospitalNS)
        self.api.add_namespace(activityNS)
        self.api.add_namespace(letterNS)
        self.api.add_namespace(volunteerNS)
        self.api.add_namespace(adviseNS)
        self.api.add_namespace(newlangNS)
        self.api.add_namespace(voiceNS)
        self.api.add_namespace(authNS)
        self.api.add_namespace(usersNS)

        self.api.db = db.AgayaDBClient()['stac']
        self.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
        self.config['KAKAO_REST_API_KEY'] = os.getenv("KAKAO_REST_API_KEY")

        self.api.tts = TTS()
