class Powerplant:
    """A class that allows to store the powerplants' information.

    """

    def __init__(self, name, type_, efficiency, pmin, pmax):
        """

        Parameters
        ----------
        name : str
            Powerplant name.
        type_ : str
            Gasfired, turbojet or windturbine.
        efficiency : float
            The efficiency at which they convert a MWh of fuel into a MWh of electrical energy. Wind-turbines do not
            consume 'fuel' and thus are considered to generate power at zero price.
        pmin : int
            The minimum amount of power the powerplant generates when switched on.
        pmax : int
            The maximum amount of power the powerplant can generate.
        """
        self.name = name
        self.type = type_
        self.efficiency = efficiency
        self.pmin = pmin
        self.pmax = pmax
        # cost to generate 1MWh of electricity
        self.real_cost = 0
