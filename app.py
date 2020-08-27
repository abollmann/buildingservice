from buildingservice import app
from buildingservice.consumer import BuildingsConsumer

from config import APP_HOST

if __name__ == '__main__':
    BuildingsConsumer().start()
    app.run(host=APP_HOST, port=5001)
