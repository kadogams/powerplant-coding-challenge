from ast import literal_eval

from flask import Flask

from .powerplant import Powerplant


POWERPLANT_TYPES = ['gasfired', 'turbojet', 'windturbine']
MIN_EFFICIENCY = 0
MAX_EFFICIENCY = 1
MIN_WIND = 0
MAX_WIND = 100


_logger = Flask(__name__).logger


class PowerDispatcher:
    errors = []

    def __init__(self, data):
        """

        Parameters
        ----------
        data : json-like dict
            HTTP request payload.
        """
        print(data)
        self.load = self._check_load(data['load'])

    ##################
    # Public Methods #
    ##################

    ###################
    # Private Methods #
    ###################

    def _check_load(self, load):
        """Check the load value of the HTTP request payload.

        Parameters
        ----------
        load
            HTTP request payload value.

        Returns
        -------
        Int, Float or None
            The load value (if an error occurred None will be returned).

        """
        if isinstance(load, (int, float)) and load >= 0:
            return load
        error = 'The load has to be a positive number.'
        _logger.error(error)
        self.errors.append(error)
        return None
