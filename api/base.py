from flask import Flask
from flask_restplus import Api
from .test import api as testNS
from .letter import api as letterNS

class AgayaApi(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.config.SWAGGER_UI_DOC_EXPANSION = 'full'

        self.api = Api(self, title="Agaya API", version='0.1')
        self.api.add_namespace(testNS)
        self.api.add_namespace(letterNS)