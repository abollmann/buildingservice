import random
import string

from buildingservice.model import Building

TOTAL_ADDRESSES = 19

fraunhofer_ids = [F'AB{i}' for i in range(1, TOTAL_ADDRESSES + 1)]
house_numbers = [random.randint(1, 100) for _ in range(TOTAL_ADDRESSES)]
city = 'Kassel'
city_codes_options = ['34123', '34131', '34132', '34128', '34355']
city_codes = [city_codes_options[random.randint(0, len(city_codes_options) - 1)] for _ in range(TOTAL_ADDRESSES)]
house_number_adds = [random.choice(string.ascii_letters).upper() if i % 2 == 0 else None for i in
                     range(TOTAL_ADDRESSES)]
streets = ['Amselweg', 'Ahornweg', 'Ackerstrasse',
           'Bergstrasse', 'Bahnhofstrasse', 'Brunnenstrasse',
           'Charlottenstrasse', 'Castroper Strasse', 'Calmontstrasse',
           'Dorfstrasse', 'Danziger Strasse', 'Drosselweg',
           'Eichendorffstrasse', 'Erlenweg', 'Eichenweg',
           'Feldstrasse', 'Finkenweg', 'Friedhofstrasse',
           'Gartenstrasse']


def generate_initial_data():
    if list(Building.objects.all()):
        return
    for internal_id, house_number, city_code, house_number_add, street in zip(fraunhofer_ids, house_numbers, city_codes,
                                                                              house_number_adds, streets):
        building = {
            'internal_id': internal_id,
            'city_code': city_code,
            'city': city,
            'house_number': house_number,
            'street': street
        }
        if house_number_add:
            building['house_number_add'] = house_number_add
        Building(**building).save()
