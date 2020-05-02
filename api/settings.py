"""
Settings and global variables for the powerplant-coding-challenge project.
"""
# import os


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# LOGGING_FILE = os.path.join(BASE_DIR, 'powerplant-coding-challenge.log')

MIN_PERCENT = 0
MAX_PERCENT = 100

MIN_EFFICIENCY = 0
MAX_EFFICIENCY = 1

FUEL_PARAMS = ['gas(euro/MWh)', 'kerosine(euro/MWh)', 'co2(euro/ton)', 'wind(%)']

POWERPLANT_PARAMS = ['name', 'type', 'efficiency', 'pmin', 'pmax']
POWERPLANT_TYPES = ['gasfired', 'turbojet', 'windturbine']

# if set to false, the API responses will contain integer values (assuming that the pmin and pmax values in the payload
# are whole numbers)
ALLOW_FLOAT = True
