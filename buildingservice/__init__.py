from collections import OrderedDict
from contextlib import suppress

from flask import Flask, logging
from flask.logging import default_handler
from flask_pymongo import PyMongo
from pymongo.errors import CollectionInvalid

from buildingservice.shared.json_encoder import ImprovedJSONEncoder
from buildingservice.shared.logging_handler import LoggingHandler
from buildingservice.schema import schema
from config import *


app = Flask(__name__)
app.config.from_pyfile('../config.py')

# LOGGING CONFIG
logger = logging.create_logger(app)
logger.removeHandler(default_handler)
logger.addHandler(LoggingHandler())

# DATABASE CONFIG
credentials = F'{MONGO_USER}:{MONGO_PASSWORD}@' if MONGO_USER and MONGO_PASSWORD else ''
auth_source = '?authSource=admin' if credentials else ''
app.config.from_mapping(
    MONGO_URI=F'mongodb://{credentials}{MONGO_HOST}:{MONGO_PORT}/{MONGO_NAME}{auth_source}',
)

mongo = PyMongo(app)
db = mongo.cx.devopsss2020

# force create the collection so we can apply the schema
with suppress(CollectionInvalid):
    db.create_collection('buildings')
cmd = OrderedDict([('collMod', 'buildings'),
                   ('validator', schema),
                   ('validationLevel', 'moderate')])

db.command(cmd)
buildings = db.buildings

json_encoder = ImprovedJSONEncoder()


