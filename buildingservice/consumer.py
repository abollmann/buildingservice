from threading import Thread

from bson import ObjectId
from kafka import KafkaConsumer

from buildingservice import logger
from buildingservice.shared.error_handlers import handle_kafka_errors
from buildingservice.model import Building
from config import KAFKA_HOST, KAFKA_PORT, KAFKA_PREFIX
from buildingservice.shared.util import parse_message


class BuildingsConsumer(Thread):
    daemon = True

    def run(self):
        consumer = KafkaConsumer(
            F'{KAFKA_PREFIX}-buildings-commands',
            bootstrap_servers=[F'{KAFKA_HOST}:{KAFKA_PORT}'],
            client_id=F'{KAFKA_PREFIX}-buildings-consumer',
            group_id=F'{KAFKA_PREFIX}-buildings-commands')

        for message in consumer:
            handle_message(message)


def handle_add(data):
    building_id = data['home_building']
    tenant_id = ObjectId(data['_id'])
    building = list(Building.objects.raw({'_id': building_id}))[0]
    tenant_ids = building.tenants + [tenant_id]
    Building.objects.raw({'_id': building_id}).update(
        {'$set': {'tenants': tenant_ids}})
    logger.warn(F'Updated {tenant_id}')


def handle_remove(data):
    pass


ALLOWED_MESSAGE_TYPES = ['ADD_TENANT', 'REMOVE_TENANT']
METHOD_MAPPING = {'ADD_TENANT': handle_add,
                  'REMOVE_TENANT': handle_remove}


@handle_kafka_errors
def handle_message(message):
    data, command_type = parse_message(message, ALLOWED_MESSAGE_TYPES)
    METHOD_MAPPING[command_type](data)
