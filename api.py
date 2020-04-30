from logging.handlers import RotatingFileHandler
import os

from flask import Flask, request
from flask_restful import Api, Resource, reqparse

from utils.power_dispatcher import PowerDispatcher


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOGGING_FILE = os.path.join(BASE_DIR, 'powerplant-coding-challenge.log')


app = Flask(__name__)
api = Api(app)

# parser = reqparse.RequestParser()
# parser.add_argument('load')
# parser.add_argument('fuels')
# parser.add_argument('powerplants')


class PowerplantCodingChallenge(Resource):
    def get(self):
        # try:
        data = request.get_json()
        dispatcher = PowerDispatcher(data)
        # except Exception as e:
        #     print(e)
        return {'hello': 'world'}


api.add_resource(PowerplantCodingChallenge, '/', '/api')


if __name__ == '__main__':
    handler = RotatingFileHandler(LOGGING_FILE, maxBytes=8096, backupCount=1)
    app.logger.addHandler(handler)
    app.run(debug=True)

# TODO README.md + requirements.txt
