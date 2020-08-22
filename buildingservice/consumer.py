from threading import Thread

from kafka import KafkaConsumer
from pymodm.errors import ValidationError

from buildingservice import logger
from buildingservice.producer import produce_data
from buildingservice.shared.error_handlers import handle_kafka_errors
from buildingservice.shared.exceptions import KafkaMessageException
from buildingservice.model import Building
from buildingservice.shared.util import parse_message
from config import KAFKA_HOST, KAFKA_PORT, KAFKA_PREFIX


class ApartmentCommandConsumer(Thread):
    daemon = True

    def run(self):
        consumer = KafkaConsumer(
            F'{KAFKA_PREFIX}-buildings-commands',
            bootstrap_servers=[F'{KAFKA_HOST}:{KAFKA_PORT}'],
            client_id=F'{KAFKA_PREFIX}-buildings-consumer',
            group_id=F'{KAFKA_PREFIX}-buildings-commands')

        for message in consumer:
            handle_message(message)


def handle_create(data, message_id):
    try:
        building = Building(**data).save().to_dict()
        logger.warn(F'Created {building}')
        return building, 201
    except ValidationError as error:
        logger.error(error.message)
        raise KafkaMessageException(error.message, message_id, 422)


def handle_get_all(data, message_id):
    data = [building.to_dict() for building in Building.objects.all()]
    logger.warn(F'Found {len(data)} entries')
    return data, 200


def handle_get_by_id(data, message_id):
    internal_id = data['internal_id']
    buildings = [building.to_dict() for building in Building.objects.raw({'_id': internal_id})]
    if not data:
        logger.warn(F'Not found: {internal_id}')
        return {}, 404
    else:
        building = buildings[0]
        logger.warn(F'Found {building}')
        return building, 200


ALLOWED_MESSAGE_TYPES = ['CREATE', 'GET_ALL', 'GET_BY_ID']
METHOD_MAPPING = {'CREATE': handle_create,
                  'GET_ALL': handle_get_all,
                  'GET_BY_ID': handle_get_by_id}


@handle_kafka_errors
def handle_message(message):
    data, command_type, message_id = parse_message(message, ALLOWED_MESSAGE_TYPES)
    response_data, status_code = METHOD_MAPPING[command_type](data, message_id)
    produce_data({'data': response_data, 'status_code': status_code, 'id': message_id})
