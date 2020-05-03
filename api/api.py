"""A REST API exposing a POST method that takes a payload as you can find in the `resource/example_payloads` directory
and that returns a json with the same structure as in `resource/example_response.json`.

Power will be allocated using a queuing system in order to have a cost efficient repartition of power across the
available powerplants. Power will be gradually allocated from the powerplant with the lowest cost to the one with the
highest cost.

For more information about the challenge please refer to the challenge resource.
"""

from api import app
from api.power_allocator import PowerAllocator

import logging

from flask import request
from flask_restful import Resource


@app.before_first_request
def _configure_logging():
    """App logger configuration. Please note that the Werkzeug logger will handle basic request/response information.
    """
    handler = app.logger.handlers[0]
    formatter = logging.Formatter(fmt="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    app.logger.setLevel(logging.INFO)


class PowerplantCodingChallenge(Resource):
    """The class inherits from Flask-RESTful Resource class in order to have easy access to multiple HTTP methods by
    defining methods on your resource.

    For more information please refer to: https://flask-restful.readthedocs.io/en/latest/index.html
    """
    def post(self):
        """Definition of the HTTP POST method. The function will return the appropriate response according to the
        request and its payload.
        """
        try:
            data = request.get_json()
            if not data:
                app.logger.info('Missing payload.')
                return {'message': 'Welcome to the Powerplant coding challenge. Please make a POST request with the '
                                   'required payload.'}, 400
            app.logger.info('Parsing the payload.')
            allocator = PowerAllocator(data)
            if allocator.errors or allocator.missing_params:
                if allocator.missing_params:
                    msg = 'The following parameters are required in the JSON body or the query string: `{}`.'\
                          .format('`, `'.join(allocator.missing_params))
                    allocator.errors.insert(0, msg)
                return {'errors': allocator.errors}, 400
            else:
                app.logger.info('Allocating power across the available powerplants.')
                results = allocator.run()
                if allocator.errors:
                    return {'errors': allocator.errors}, 400
                app.logger.info('Allocation of power complete.')
                return results
        except Exception as e:
            app.logger.critical(e)
            error = 'An unexpected problem occurred. Please contact the administrator if the problem persists.'
            allocator.errors.insert(0, msg)
            return {'errors': allocator.errors}, 400
