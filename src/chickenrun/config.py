import os
import json
from jsonschema import validate, ValidationError, SchemaError


class Config():
    def __init__(self, confPath=os.environ.get("CHICKENRUN_CONF_PATH", "./conf-sample.json"), schemaPath=os.environ.get("CHICKENRUN_CONF_SCHEMA_PATH", "./conf-schema.json")):
        self.confPath = confPath
        self.schemaPath = schemaPath
        self._config = None
        self.__loadConfig()

    def get(self):
        return self._config

    def refresh(self):
        self.__loadConfig()
        return self._config

    def __loadConfig(self):
        with open(self.confPath) as json_file:
            chickenHouseConfig = json.load(json_file)
        with open(self.schemaPath) as json_file:
            chickenHouseConfigSchema = json.load(json_file)
        # Raise exception if config do not validate schema
        validate(chickenHouseConfig, chickenHouseConfigSchema)
        self._config = chickenHouseConfig
