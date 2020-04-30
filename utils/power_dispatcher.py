from ast import literal_eval

from flask import Flask

from .powerplant import Powerplant


FUEL_PARAMS = ['gas(euro/MWh)', 'kerosine(euro/MWh)', 'co2(euro/ton)', 'wind(%)']
POWERPLANT_PARAMS = ['name', 'type', 'efficiency', 'pmin', 'pmax']
POWERPLANT_TYPES = ['gasfired', 'turbojet', 'windturbine']
MIN_EFFICIENCY = 0
MAX_EFFICIENCY = 1
MIN_WIND = 0
MAX_WIND = 100


_logger = Flask(__name__).logger


class PowerDispatcher:

    def __init__(self, data):
        """

        Parameters
        ----------
        data : json-like dict
            HTTP request payload.
        """
        # print(data)
        self.errors = []
        self.missing_params = []
        self.load = self._check_load(data)
        self.gas_cost, self.kerosine_cost, self.co2_cost, self.wind = self._check_fuels(data)

    ##################
    # Public Methods #
    ##################

    def run(self):
        pass

    ###################
    # Private Methods #
    ###################

    def _check_fuels(self, data):
        """Check the fuel values of the HTTP request payload.

        Parameters
        ----------
        data
            HTTP request payload.

        Returns
        -------
        Tuple4
            The gas, kerosine, CO2 and wind values.

        """
        if 'fuels' not in data:
            self.missing_params.append('fuels')
            return None, None, None, None

        def _check_fuel_param(fuels, fuel_param):
            if fuel_param in fuels:
                param = fuels[fuel_param]
                if fuel_param == 'wind(%)' and isinstance(param, (int, float)) and (param < 0 or param > 100):
                    error = 'The `fuel.wind(%)` value has to be between 0 and 100.'
                    _logger.error(error)
                    self.errors.append(error)
                elif not isinstance(param, (int, float)) or param < 0:
                    error = f'The `fuel.{fuel_param}` value has to be a positive number.'
                    _logger.error(error)
                    self.errors.append(error)
            else:
                self.missing_params.append(f'fuels.{fuel_param}')
                param = None
            return param

        fuels = data['fuels']
        gas_cost = _check_fuel_param(fuels, FUEL_PARAMS[0])
        kerosine_cost = _check_fuel_param(fuels, FUEL_PARAMS[1])
        co2_cost = _check_fuel_param(fuels, FUEL_PARAMS[2])
        wind = _check_fuel_param(fuels, FUEL_PARAMS[3])
        return gas_cost, kerosine_cost, co2_cost, wind

    def _check_load(self, data):
        """Check the load value of the HTTP request payload.

        Parameters
        ----------
        data
            HTTP request payload.

        Returns
        -------
        Int, Float or None
            The load value (if an error occurred None will be returned).

        """
        if 'load' not in data:
            self.missing_params.append('load')
            return None
        load = data['load']
        if isinstance(load, (int, float)) and load >= 0:
            return load
        error = 'The `load` value has to be a positive number.'
        _logger.error(error)
        self.errors.append(error)
        return None
