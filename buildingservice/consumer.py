import json
from threading import Thread

from kafka import KafkaConsumer
from pymodm.errors import ValidationError

from buildingservice import logger
from buildingservice.producer import produce_data
from buildingservice.shared.error_handlers import handle_kafka_errors
from buildingservice.shared.exceptions import KafkaMessageException
from buildingservice.model import Building
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


@handle_kafka_errors
def handle_message(message):
    message = json.loads(message.value.decode('utf-8'))
    message_id = message['id']
    if not all(key in message for key in ['command_type', 'data']):
        raise KafkaMessageException('JSON-Object with "id", "command_type" and "data" expected.', message_id)

    command_type = message['command_type']
    if not any(command == command_type for command in ['CREATE', 'GET_ALL', 'GET_BY_ID']):
        raise KafkaMessageException('command_type must be either "CREATE", "GET_ALL", "GET_BY_ID", "GET_BY_FILTER".',
                                    message_id)

    data = message['data']
    status_code = 200
    if command_type == 'CREATE':
        data = json.loads(data)
        try:
            building = Building(**data).save().to_dict()
            message['data'] = building
            logger.warn(F'Created {building}')
        except ValidationError as error:
            logger.error(error.message)
            raise KafkaMessageException(error.message, message_id, 422)

    elif command_type == 'GET_ALL':
        data = [building.to_dict() for building in Building.objects.all()]
        logger.warn(F'Found {len(data)} entries')

    elif command_type == 'GET_BY_ID':
        internal_id = data['internal_id']
        data = [building.to_dict() for building in Building.objects.raw({'_id': internal_id})]
        if not data:
            status_code = 404
        else:
            data = data[0]
        logger.warn(F'Found {data}')

    message['data'] = data
    message['status_code'] = status_code
    produce_data(message)
