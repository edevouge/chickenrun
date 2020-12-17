import logging
from signal import pause

from config import Config
from chickenhouse import ChickenHouse


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(threadName)s %(message)s')

    # load chickenHouseConfig from file
    conf = Config()
    chickenHouseConfig = conf.get()

    chickenHouse = ChickenHouse(chickenHouseConfig)
    pause()
