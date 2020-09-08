from flask import Flask
from flask_restplus import Api
from .test import api as testNS
from .medicine import api as medicineNS
from .hospital import api as hospitalNS
from .letter import api as letterNS
from .auth import api as authNS
import db
import os

class AgayaApi(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.config.SWAGGER_UI_DOC_EXPANSION = 'list'

        self.api = Api(self, title="Agaya API", version='0.2', authorizations={
            'jwt': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization'
            }
        })
        self.api.add_namespace(testNS)
        self.api.add_namespace(medicineNS)
        self.api.add_namespace(hospitalNS)
        self.api.add_namespace(letterNS)
        self.api.add_namespace(authNS)

        self.api.db = db.AgayaDBClient()['stac']
        self.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
