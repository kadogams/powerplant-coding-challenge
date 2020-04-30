from logging.handlers import RotatingFileHandler
import os

from flask import Flask
from flask_restful import Resource, Api


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOGGING_FILE = os.path.join(BASE_DIR, 'powerplant-coding-challenge.log')


app = Flask(__name__)
api = Api(app)


class PowerplantCodingChallenge(Resource):
    def get(self):
        app.logger.debug('test')
        app.logger.info('test2')
        app.logger.warning('test3')
        return {'hello': 'world'}


api.add_resource(PowerplantCodingChallenge, '/')


if __name__ == '__main__':
    handler = RotatingFileHandler(LOGGING_FILE, maxBytes=8096, backupCount=1)
    app.logger.addHandler(handler)
    app.run(debug=True)

# TODO README.md + requirements.txt
