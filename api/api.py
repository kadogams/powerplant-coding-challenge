import logging
from pprint import pprint

from flask import Flask, request
from flask_restful import Api, Resource

from api import app, api
from .power_dispatcher import PowerDispatcher


# parser = reqparse.RequestParser()
# parser.add_argument('aaa', required=True)
# parser.add_argument('bbb', required=True)


class PowerplantCodingChallenge(Resource):
    def get(self):
        # try:
        # parser.parse_args()
        data = request.get_json()
        if not data:
            return {'message': 'Welcome to the Powerplant coding challenge. Please make a GET request with the '
                               'required payload.'}, 400
        dispatcher = PowerDispatcher(data)
        # pprint(vars(dispatcher))

        if not dispatcher.errors and not dispatcher.missing_params:
            pass
        else:
            if dispatcher.missing_params:
                msg = 'The following parameters are required in the JSON body or the query string: `{}`.'\
                      .format('`, `'.join(dispatcher.missing_params))
                dispatcher.errors.insert(0, msg)
            return {'errors': dispatcher.errors}, 400

        # except Exception as e:
        #     print(e)
        return {'hello': 'world'}


# api.add_resource(PowerplantCodingChallenge, '/', '/api')


# if __name__ == '__main__':
#     handler = logging.handlers.RotatingFileHandler(LOGGING_FILE, maxBytes=8096, backupCount=1)
#     formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
#     handler.setFormatter(formatter)
#     handler.setLevel(logging.INFO)
#     app.logger.addHandler(handler)
#     app.run(debug=True)

# TODO README.md + requirements.txt
