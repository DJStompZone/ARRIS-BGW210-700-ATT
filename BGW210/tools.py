from typing import Tuple, Union
from traceback import print_exc, format_exc
import os
import json

from bs4 import BeautifulSoup
from requests import Response
from bs4.element import ResultSet

from .Config import Config, ConfigError


class Tools:
    class Network:
        @classmethod
        def resolve_ip(cls) -> str:
            pass

        @classmethod
        def resolve_secure(cls) -> str:
            if True:
                return 'http://'
            else:
                return 'https://'
        
        @classmethod
        def load_credentials_from_json(cls, jsonfile) -> dict[str, str]:
            if not os.path.isfile(jsonfile):
                raise FileNotFoundError(f"The specified JSON file could not be loaded: {jsonfile}")
            with open(jsonfile) as fp:
                return json.loads(fp.read())
        
        @classmethod
        def get_credentials(cls) -> Union["Config", "ConfigError"]:
            default_credentials_path = os.path.normpath(os.path.expanduser("~/.bgw210rc.json"))
            config_keys = _keys =  ["url", "username", "password"]
            try:
                _credentials = cls.load_credentials_from_json(default_credentials_path)
                config_values = map(_credentials.get, config_keys)
                _cfg = dict(zip(config_keys, list(config_values)))
                if None not in config_values:
                    return Config(**_cfg)
                missing = list(filter(lambda k: _cfg[k] is None, _cfg))
                raise ValueError(f"Missing required value(s) from config file: {missing}")
            except (FileNotFoundError, KeyError, ValueError) as e:
                tb = traceback.format_exc()
                print(f"{e} encountered while loading saved config:")
                print(tb)
                return ConfigError(str(e), tb)

        def login_required(self) -> bool:
            raise NotImplementedError

        # if html_body.find('title').text == 'Login':

    class Parser:
        @staticmethod
        def get_nonce(response: Response) -> str:
            return BeautifulSoup(response.content, features="html.parser").find('input').attrs.get('value')

        @staticmethod
        def get_table_data(response: Response) -> ResultSet:
            rows = BeautifulSoup(response.content, features="html.parser").findAll('tr')
            return rows

        @staticmethod
        def get_field(response: Response, fields: list) -> dict:
            data = {}
            html_body = BeautifulSoup(response.content, features="html.parser")
            for field in fields:
                data[field] = html_body.find('input', {"name": field}).attrs.get('value')
            return data

        @classmethod
        def parse_fields(cls, response: Response) -> dict:
            data = {}
            rows = cls.get_table_data(response)
            for row in rows:
                try:
                    data[row.find('th').text.split('Default')[0]] = row.find('td').find('input').attrs.get('value')
                except AttributeError:
                    pass
            return data
