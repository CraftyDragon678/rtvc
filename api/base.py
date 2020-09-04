from flask import Flask
from flask_restplus import Api

class AgayaApi(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.config.SWAGGER_UI_DOC_EXPANSION = 'full'

        self.api = Api(self, title="Agaya API", version='0.1')