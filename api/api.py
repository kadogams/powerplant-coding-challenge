from api import app

from flask import Flask, request
from flask_restful import Api, Resource

from .power_allocator import PowerAllocator


class PowerplantCodingChallenge(Resource):
    def get(self):
        # try:
        data = request.get_json()
        if not data:
            return {'message': 'Welcome to the Powerplant coding challenge. Please make a GET request with the '
                               'required payload.'}, 400
        allocator = PowerAllocator(data)
        # pprint(vars(allocator))

        if allocator.errors or allocator.missing_params:
            if allocator.missing_params:
                msg = 'The following parameters are required in the JSON body or the query string: `{}`.'\
                      .format('`, `'.join(allocator.missing_params))
                allocator.errors.insert(0, msg)
            return {'errors': allocator.errors}, 400
        else:
            allocator.run()

        # except Exception as e:
        #     print(e)
        return {'hello': 'world'}
