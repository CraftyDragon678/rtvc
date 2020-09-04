from flask import Flask
from flask_restplus import Resource, Api


class AgayaApi(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.config.SWAGGER_UI_DOC_EXPANSION = 'full'

        self.api = Api(self)