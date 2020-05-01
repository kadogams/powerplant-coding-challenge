from api import app
from api.powerplant import Powerplant


MIN_PERCENT = 0
MAX_PERCENT = 100
MIN_EFFICIENCY = 0
MAX_EFFICIENCY = 1
FUEL_PARAMS = ['gas(euro/MWh)', 'kerosine(euro/MWh)', 'co2(euro/ton)', 'wind(%)']
POWERPLANT_PARAMS = ['name', 'type', 'efficiency', 'pmin', 'pmax']
POWERPLANT_TYPES = ['gasfired', 'turbojet', 'windturbine']


class PowerAllocator:
    """A class that allows to parse the payload and allocate resources accordingly.
    """

    def __init__(self, data):
        """The class will initialized with the following attributes:
        - load: the load is the amount of energy (MWh) that need to be generated during one hour.
        - gas_price: the price of gas per MWh. Thus if gas is at 6 euro/MWh and if the efficiency of the powerplant is
          50% (i.e. 2 units of gas will generate one unit of electricity), the cost of generating 1 MWh is 12 euro.
        - kerosine_price: the price of kerosine per MWh.
        - co2_price: the price of emission allowances (optionally to be taken into account).
        - wind: percentage of wind. Example: if there is on average 25% wind during an hour, a wind-turbine with a Pmax
          of 4 MW will generate 1MWh of energy.
        - powerplants: a list of Powerplant objects.


        Parameters
        ----------
        data : json-like dict
            HTTP request payload.
        """
        self.errors = []
        self.missing_params = []
        self.load = self._parse_load(data)
        self.gas_price, self.kerosine_price, self.co2_price, self.wind = self._parse_fuels(data)
        self.powerplants = self._parse_powerplants(data)

    ##################
    # Public Methods #
    ##################

    def run(self):
        """Allocate power resources across the powerplants and return a list with the result.

        Returns
        -------
        list
            A list of dict containing the name and the power delivered by each powerplant.
        """
        if self.errors or self.missing_params:
            error = 'An error occurred during the parsing of the payload, the resources cannot be allocated.'
            app.logger.error(error)

        self._get_real_costs()

    ###################
    # Private Methods #
    ###################

    def _get_real_costs(self):
        """Get the cost to generate 1MWh of electricity for every powerplant and store the value in their `real_cost`
        attribute.
        """
        for powerplant in self.powerplants:
            if powerplant.type == 'gasfired':
                powerplant.real_cost = self.gas_price / powerplant.efficiency
            elif powerplant.type == 'turbojet':
                powerplant.real_cost = self.kerosine_price / powerplant.efficiency
            elif powerplant.type == 'windturbine':
                powerplant.real_cost = 0

    def _parse_fuels(self, data):
        """Parse the fuel values of the HTTP request payload.

        Parameters
        ----------
        data : json-like dict
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
                value = fuels[fuel_param]
                error = None
                if fuel_param == 'wind(%)' and (not isinstance(value, (int, float))
                                                or value < MIN_PERCENT
                                                or value > MAX_PERCENT):
                    error = f'The `fuels.wind(%)` value must be a number between {MIN_PERCENT} and {MAX_PERCENT}.'
                elif not isinstance(value, (int, float)) or value < 0:
                    error = f'The `fuels.{fuel_param}` value must be a positive number.'
                if error:
                    app.logger.error(error)
                    self.errors.append(error)
            else:
                self.missing_params.append(f'fuels.{fuel_param}')
                value = None
            return value

        fuels = data['fuels']
        gas_price = _check_fuel_param(fuels, FUEL_PARAMS[0])
        kerosine_price = _check_fuel_param(fuels, FUEL_PARAMS[1])
        co2_price = _check_fuel_param(fuels, FUEL_PARAMS[2])
        wind = _check_fuel_param(fuels, FUEL_PARAMS[3])
        return gas_price, kerosine_price, co2_price, wind

    def _parse_load(self, data):
        """Parse the load value of the HTTP request payload.

        Parameters
        ----------
        data
            HTTP request payload.

        Returns
        -------
        int, float or None
            The load value (if an error occurred None will be returned).
        """
        if 'load' not in data:
            self.missing_params.append('load')
            return None
        load = data['load']
        if isinstance(load, (int, float)) and load >= 0:
            return load
        error = 'The `load` value must be a positive number.'
        app.logger.error(error)
        self.errors.append(error)
        return None

    def _parse_powerplants(self, data):
        """Parse the powerplant values of the HTTP request payload.

        Parameters
        ----------
        data
            HTTP request payload.

        Returns
        -------
        List
            A list of Powerplant objects.
        """
        if 'powerplants' not in data:
            self.missing_params.append('powerplants')
            return []

        def _check_powerplant_param(powerplant, powerplant_param):
            if powerplant_param in powerplant:
                value = powerplant[powerplant_param]
                error = None
                if powerplant_param == 'name' and not isinstance(value, str):
                    error = 'The `powerplants.name` value must be a string.'
                    app.logger.error(error)
                    self.errors.append(error)
                elif powerplant_param == 'type' and value not in POWERPLANT_TYPES:
                    error = "Valid values for the powerplant types are '{}', "\
                            "the given value is invalid: '{}'"\
                            .format("', '".join(POWERPLANT_TYPES), value)
                elif powerplant_param == 'efficiency' and (not isinstance(value, (int, float))
                                                           or value < MIN_EFFICIENCY
                                                           or value > MAX_EFFICIENCY):
                    error = f'The `powerplants.efficiency` value must be a number between {MIN_EFFICIENCY} and '\
                            f'{MAX_EFFICIENCY}.'
                elif (powerplant_param == 'pmin' or powerplant_param == 'pmax') and (not isinstance(value, (int, float))
                                                                                     or value < 0):
                    error = f'The `powerplants.{powerplant_param}` value has to be a positive number.'
                if error:
                    app.logger.error(error)
                    self.errors.append(error)
            else:
                self.missing_params.append(f'powerplants.{powerplant_param}')
                value = None
            return value

        powerplants = data['powerplants']
        objects = {}
        for powerplant in powerplants:
            name = _check_powerplant_param(powerplant, POWERPLANT_PARAMS[0])
            type_ = _check_powerplant_param(powerplant, POWERPLANT_PARAMS[1])
            efficiency = _check_powerplant_param(powerplant, POWERPLANT_PARAMS[2])
            pmin = _check_powerplant_param(powerplant, POWERPLANT_PARAMS[3])
            pmax = _check_powerplant_param(powerplant, POWERPLANT_PARAMS[4])
            # check if the name is already used
            if name in objects:
                error = 'The names of the powerplants must be unique.'
                app.logger.error(error)
                self.errors.append(error)
            # check if pmin is higher than pmax
            if pmin > pmax:
                error = f"The `pmin` value of powerplant '{name}' is higher than `pmax`."
                app.logger.error(error)
                self.errors.append(error)
            objects[name] = Powerplant(name, type_, efficiency, pmin, pmax)
        return objects.values()
