from typing import Tuple

from bs4 import BeautifulSoup
from requests import Response
from bs4.element import ResultSet
from Config import Config


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
        def set_credentials(cls) -> Tuple[str, str, str]:
            if True:
                credentials = Config.BGW210.Credentials.Remote
            else:
                credentials = Config.BGW210.Credentials.Remote
            return credentials.url, credentials.username, credentials.password

        def login_required(self) -> bool:
            pass

        # if html_body.find('title').text == 'Login':

    class Parser:
        @staticmethod
        def get_nonce(response: Response) -> str:
            return BeautifulSoup(response.content, features="html.parser").find('input').attrs.get('value')

        @staticmethod
        def get_table_data(response: Response) -> ResultSet:
            rows = BeautifulSoup(response.content, features="html.parser").findAll('tr')
            return rows
