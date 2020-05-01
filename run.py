from api import app
from api.api import PowerplantCodingChallenge

import logging
from logging.handlers import RotatingFileHandler
import os

from flask_restful import Api


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGGING_FILE = os.path.join(BASE_DIR, 'powerplant-coding-challenge.log')


if __name__ == '__main__':
    handler = logging.handlers.RotatingFileHandler(LOGGING_FILE, maxBytes=8096, backupCount=1)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    api = Api(app)
    api.add_resource(PowerplantCodingChallenge, '/', '/api')

    app.run(debug=True)

# TODO README.md + requirements.txt
