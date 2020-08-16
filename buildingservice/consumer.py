import json
from threading import Thread

from bson import ObjectId
from bson.errors import InvalidId
from kafka import KafkaConsumer
from pymongo.errors import WriteError

from buildingservice import buildings, logger
from buildingservice.producer import produce_data
from buildingservice.shared.error_handlers import handle_kafka_errors
from buildingservice.shared.exceptions import KafkaMessageException
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
    if not any(command == command_type for command in ['CREATE', 'GET_ALL', 'GET_BY_ID', 'GET_BY_FILTER']):
        raise KafkaMessageException('command_type must be either "CREATE", "GET_ALL", "GET_BY_ID", "GET_BY_FILTER".',
                                    message_id)

    data = message['data']
    status_code = 200
    if command_type == 'CREATE':
        try:
            message['data'] = buildings.insert(json.loads(data))
        except WriteError:
            raise KafkaMessageException(F'Validation failed for {data}. Reference API docs.', message_id, 422)
        status_code = 201
        logger.warn(F'Created {data}')

    if command_type == 'GET_ALL':
        data = list(buildings.find())
        logger.warn(F'Found {len(data)} entries')

    if command_type == 'GET_BY_ID':
        object_id = data['_id']
        try:
            object_id = ObjectId(object_id)
        except (InvalidId, TypeError, AssertionError):
            raise KafkaMessageException(F'Invalid ObjectId: {object_id}', message_id)
        data = list(buildings.find({"_id": ObjectId(object_id)}))
        logger.warn(F'Found {data}')

    if command_type == 'GET_BY_FILTER':
        data = buildings.find({json.dumps(data)})
        logger.warn(F'Found {len(data)} entries')

    message['data'] = data
    message['status_code'] = status_code
    produce_data(message)
