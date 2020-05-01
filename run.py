from api import app
from api.api import PowerplantCodingChallenge

import logging
from logging.handlers import RotatingFileHandler
import os

from flask_restful import Api


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGGING_FILE = os.path.join(BASE_DIR, 'powerplant-coding-challenge.log')


if __name__ == '__main__':
    # app logger config
    handler = logging.handlers.RotatingFileHandler(LOGGING_FILE, maxBytes=65536, backupCount=1)
    formatter = logging.Formatter(fmt="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # log messages emitted by Werkzeug will also be saved in the file
    internal_logger = logging.getLogger('werkzeug')
    internal_logger.setLevel(logging.INFO)
    internal_logger.addHandler(handler)

    api = Api(app)
    api.add_resource(PowerplantCodingChallenge, '/', '/api')

    app.run(debug=True)

# TODO README.md + requirements.txt
