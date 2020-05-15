from api import app
from api.settings import *
from api.powerplant import Powerplant

import copy


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
        - wind_percent: percentage of wind. Example: if there is on average 25% wind during an hour, a wind-turbine with a Pmax
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
        self.gas_price, self.kerosine_price, self.co2_price, self.wind_percent = self._parse_fuels(data)
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
            return []

        # get the cost to generate 1MWh of electricity for each powerplant
        self._get_real_costs()

        # sort powerplants by their real_cost in ascending order
        self.powerplants.sort(key=lambda x: x.real_cost)

        return self._allocate_power()

    ###################
    # Private Methods #
    ###################

    def _allocate_power(self):
        """Allocate power resources across the powerplants.

        A queuing system with dicts containing a snapshot of the power allocation will be used:
        - p_list: list of allocated power, the index corresponding to the index of self.powerplants
        - curr_index: index of the powerplant to be reallocated during in the queuing process

        An empty allocation snapshot will be initialized, and power will be gradually allocated from the powerplant
        with the lowest cost to the one with the highest cost (self.powerplants have been sorted by their `real_cost`
        attribute in ascending order). The function iterates until no elements are found in the queue.

        Returns
        -------
        list
            A list of dict containing the name and the power delivered by each powerplant.
        """
        # number of powerplants
        size = len(self.powerplants)

        # initialize an allocation snapshot
        allocation = {
            'p_list': [0] * size,
            'curr_index': 0
        }

        def _reallocate(allocation, new_power, new_index):
            """Update and return a new allocation snapshot.
            """
            curr_index = allocation['curr_index']
            new_allocation = copy.deepcopy(allocation)
            new_allocation['p_list'][curr_index] = new_power
            new_allocation['curr_index'] = new_index
            return new_allocation

        def _get_total_cost(allocation, size):
            """Return the total cost of the current allocation.
            """
            total_cost = 0
            for i in range(size):
                total_cost += allocation['p_list'][i] * self.powerplants[i].real_cost
            return total_cost

        # once the target load reached, the allocation snapshot will be saved in this variable
        fully_allocated = None
        queue = [allocation]
        while queue:
            # get the current snapshot from the queue
            allocation = queue.pop(0)

            curr_index = allocation['curr_index']
            total_power = sum(allocation['p_list'])
            remaining_load = self.load - total_power

            if remaining_load == 0:  # power allocated correctly
                total_cost = _get_total_cost(allocation, size)
                # replace the current fully_allocated object if the new one is more cost efficient
                if not fully_allocated or fully_allocated['total_cost'] > total_cost:
                    fully_allocated = allocation
                    fully_allocated['total_cost'] = total_cost
                continue
            elif not 0 <= curr_index < size:  # ignore queue element if current index is out of reach
                continue

            # power limits of the current powerplant
            curr_pmin = self.powerplants[curr_index].pmin
            curr_pmax = self.powerplants[curr_index].pmax

            if remaining_load > 0:  # under power
                if remaining_load >= curr_pmax:
                    new_power = curr_pmax
                elif remaining_load >= curr_pmin:
                    new_power = remaining_load
                else:  # required power lower than the current powerplant's pmin
                    new_power = 0
                    # add a different scenario to the queue: allocate pmin and try to decrease
                    # the power of the previous index
                    new_allocation = _reallocate(allocation=allocation, new_power=curr_pmin, new_index=curr_index - 1)
                    queue.append(new_allocation)
                new_allocation = _reallocate(allocation=allocation, new_power=new_power, new_index=curr_index + 1)
                queue.append(new_allocation)

            else:  # over power
                excess_load = abs(remaining_load)
                curr_power = allocation['p_list'][curr_index]
                if excess_load >= curr_pmax:
                    new_power = 0
                elif curr_power - excess_load >= curr_pmin:
                    new_power = curr_power - excess_load
                else:  # required power lower than the current powerplant's pmin
                    new_power = 0
                    if curr_pmin != 0:
                        # add a different scenario to the queue: allocate pmin and try to decrease
                        # the power of the previous index
                        new_allocation = _reallocate(allocation=allocation, new_power=curr_pmin, new_index=curr_index - 1)
                        queue.append(new_allocation)
                new_allocation = _reallocate(allocation=allocation, new_power=new_power, new_index=curr_index - 1)
                queue.append(new_allocation)

        results = []
        if not fully_allocated:
            error = 'Power could not be allocated correctly, please verify the payload.'
            app.logger.error(error)
            self.errors.append(error)
        else:
            for i, powerplant in enumerate(self.powerplants):
                results.append({
                    'name': powerplant.name,
                    'p': fully_allocated['p_list'][i]
                })
        return results

    def _get_real_costs(self):
        """Get the cost to generate 1MWh of electricity for every powerplant and store the value in their `real_cost`
        attribute. The `pmax` value of the windturbine will be updated according to the wind percentage.
        """
        for powerplant in self.powerplants:
            if powerplant.type == 'gasfired':
                powerplant.real_cost = self.gas_price / powerplant.efficiency
            elif powerplant.type == 'turbojet':
                powerplant.real_cost = self.kerosine_price / powerplant.efficiency
            elif powerplant.type == 'windturbine':
                powerplant.real_cost = 0
                # adjust the pmax of windturbines according to the percentage of wind
                powerplant.pmax = powerplant.pmax * self.wind_percent / 100
                # convert to int if the ALLOW_FLOAT flag is active or if it is a whole number
                if not ALLOW_FLOAT or powerplant.pmax.is_integer():
                    powerplant.pmax = int(powerplant.pmax)

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
        wind_percent = _check_fuel_param(fuels, FUEL_PARAMS[3])
        return gas_price, kerosine_price, co2_price, wind_percent

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
        objects = []
        for powerplant in powerplants:
            name = _check_powerplant_param(powerplant, POWERPLANT_PARAMS[0])
            type_ = _check_powerplant_param(powerplant, POWERPLANT_PARAMS[1])
            efficiency = _check_powerplant_param(powerplant, POWERPLANT_PARAMS[2])
            pmin = _check_powerplant_param(powerplant, POWERPLANT_PARAMS[3])
            pmax = _check_powerplant_param(powerplant, POWERPLANT_PARAMS[4])

            # update: sharing the same name is allowed (cf. example_response.json)
            # # check if the name is already used
            # if name in [o.name for o in objects]:
            #     error = f"The name of the powerplants must be unique: '{name}' is already used."
            #     app.logger.error(error)
            #     self.errors.append(error)

            # check if pmin is higher than pmax
            if pmin > pmax:
                error = f"The `pmin` value of powerplant '{name}' is higher than `pmax`."
                app.logger.error(error)
                self.errors.append(error)
            objects.append(
                Powerplant(name, type_, efficiency, pmin, pmax)
            )
        return objects
