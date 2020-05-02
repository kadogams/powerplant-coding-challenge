from flask import Flask
from flask_restful import Api

app = Flask(__name__)

from api.api import PowerplantCodingChallenge

api = Api(app)
api.add_resource(PowerplantCodingChallenge, '/', '/api/v0')
