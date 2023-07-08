import time

import urllib3
from bs4 import BeautifulSoup
from requests import Session, Response
from Config import Config
from typing import List, Literal
from hashlib import md5
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)


class BGW210:
    def __init__(self):
        self.session = Session()

    class Device:
        class DeviceList:
            def clear_and_rescan_for_devices(self):
                pass

            def get_devices(self) -> List[dict]:
                pass

        class SystemInformation:
            def get_info(self):
                pass

        class AccessCode:
            def use_default_access_code(self):
                pass

            def update_access_code(self, new_access_code: str):
                pass

        class RemoteAccess:
            pass

        class RestartDevice:
            def restart(self):
                a = Config.BGW210.Credentials.device_access_code

            def cancel(self):
                pass

    class Broadband:
        class Status:
            def get_status(self):
                pass

        class Configure:

            def set(self, broadband_source_override: Literal[
                'Auto', 'DSL - Line 1', 'DSL - Line 2', 'DSL - Line 1 / Line 2', 'Ethernet'] = 'Auto',
                    base_mtu: int = 1500, ipv6_mtu: int = 1500):
                pass

    class HomeNetwork:
        class Status:
            def get_status(self):
                pass

        class Configure:
            dropdown = Config.BGW210.DropdownOptions

            def ethernet(self, port_1: dropdown.ethernet, port_2: dropdown.ethernet, port_3: dropdown.ethernet,
                         port_4: dropdown.ethernet):
                pass

            def mdi_x(self, port_1: dropdown.auto_on_off, port_2: dropdown.auto_on_off, port_3: dropdown.auto_on_off,
                      port_4: dropdown.auto_on_off):
                pass

        class IPv6:
            dropdown = Config.BGW210.DropdownOptions

            def set(self, ipv6: dropdown.on_off, dhcp_v6: dropdown.on_off, dhcp_v6_prefix_delegation: dropdown.on_off,
                    router_advertisement_mtu: int = 1500):
                pass

        class WiFi:
            pass

        class MACFiltering:
            pass

        class SubnetsDCHP:
            pass

        class IPAllocation:
            pass

    class Voice:
        class Status:
            pass

        class LineDetails:
            pass

        class CallStatistics:
            pass

    class Firewall:
        class Status:
            pass

        class PacketFilter:
            pass

        class NATGaming:
            pass

        class PublicSubnetHosts:
            pass

        class IPPassthrough:
            pass

        class FirewallAdvanced:
            pass

        class SecurityOptions:
            pass

    class Diagnostics:
        class Troubleshoot:
            pass

        class SpeedTest:
            pass

        class Logs:
            pass

        class Update:
            pass

        class Resets:
            pass

        class Syslog:
            pass

        class EventNotification:
            pass

        class NATTable:
            pass

    def login(self) -> Response:
        response = self.session.get(url=f'{Config.BGW210.remote_url}', verify=False)
        html_body = BeautifulSoup(response.content)
        nonce = html_body.find('nonce')
        data = {'nonce': html_body.get('nonce'),
                'password': '*' * len(Config.BGW210.Credentials.device_access_code),
                'hashpassword': md5(Config.BGW210.Credentials.device_access_code + html_body.get('nonce')),
                'Continue': 'Continue'}
        self.session.post(url=f'{Config.BGW210.base_url}/cgi-bin/login.ha')

    def logout(self) -> Response:
        pass


BGW210().login()
