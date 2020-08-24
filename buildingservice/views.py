from buildingservice import app, logger
from buildingservice.model import Building
from buildingservice.shared.json_encoder import encode_json

BUILDINGS_BASE_PATH = '/api/buildings'


@app.route(BUILDINGS_BASE_PATH, methods=['GET'])
def get_all():
    data = [building.to_dict() for building in Building.objects.all()]
    logger.warn(F'Found {len(data)} entries')
    return encode_json(data), 200
