import re

from pymodm import fields, MongoModel
from pymodm.errors import ValidationError


def validate_city_code(city_code):
    if not re.fullmatch(r'^[0-9]{5}$', city_code):
        raise ValidationError('Must be exactly 5 numbers.')


def validate_internal_id(internal_id):
    if not re.fullmatch(r'^AB(([1-9])|([1][0-9]))$', internal_id):
        raise ValidationError('Invalid.')
    if list(Building.objects.raw({'_id': internal_id})):
        raise ValidationError('Must be unique.')


class Building(MongoModel):
    # building id from fraunhofer api
    internal_id = fields.CharField(primary_key=True, validators=[validate_internal_id])
    street = fields.CharField(required=True)
    city = fields.CharField(required=True)
    city_code = fields.CharField(required=True, validators=[validate_city_code])
    house_number = fields.CharField(required=True)
    house_number_add = fields.CharField(min_length=1, max_length=1)

    def to_dict(self):
        as_dict = self.to_son().to_dict()
        del as_dict['_cls']
        return as_dict
