from __future__ import annotations

from hashlib import md5
from typing import List, Literal

import urllib3
from bs4 import BeautifulSoup
from requests import Response, Session
from urllib3.exceptions import InsecureRequestWarning

from Exceptions import CredentialsError
from Menus import DropdownOptions
from tools import Tools

urllib3.disable_warnings(InsecureRequestWarning)


class Module:
    def __init__(self, bgw210: BGW210):
        self.bgw210 = bgw210


class BGW210:
    def __init__(self, ip: str = None, port: int = None, username: str = None, password: str = None) -> None:
        self.session = Session()
        self.current_page = Response()
        url = f'{Tools.Network.resolve_secure()}{ip}:{port}'
        if not all([ip, port, username, password]):
            url, username, password = Tools.Network.set_credentials()
        self.url = url
        self.username = username
        self.password = password
        self.login()
        self.Device = self.Device(self)
        self.Broadband = self.Broadband(self)
        self.HomeNetwork = self.HomeNetwork(self)
        self.Voice = self.Voice(self)
        self.Firewall = self.Firewall(self)
        self.Diagnostics = self.Diagnostics(self)

    def __del__(self):
        self.logout()
        self.session.close()

    class Device:
        def __init__(self, bgw210: BGW210):
            self.Status = self.Status(bgw210)
            self.DeviceList = self.DeviceList(bgw210)
            self.SystemInformation = self.SystemInformation(bgw210)
            self.AccessCode = self.AccessCode(bgw210)
            self.RemoteAccess = self.RemoteAccess(bgw210)
            self.RestartDevice = self.RestartDevice(bgw210)

        class Status(Module):
            pass

        class DeviceList(Module):

            def clear_and_rescan_for_devices(self) -> dict:
                url = f'{self.bgw210.url}/cgi-bin/devices.ha'
                data = {'nonce': Tools.Parser.get_nonce(self.bgw210.session.get(url)),
                        'Clear': 'Clear and Rescan for Devices'}
                self.bgw210.current_page = self.bgw210.session.post(url=url, data=data)
                return self.get_devices(False)

            def get_devices(self, refresh: bool = True) -> dict:
                if refresh:
                    url = f'{self.bgw210.url}/cgi-bin/devices.ha'
                    self.bgw210.current_page = self.bgw210.session.get(url)
                table = {}
                cache = {}
                rows = Tools.Parser.get_table_data(self.bgw210.current_page)
                for row in rows:
                    row = [r for r in row.text.split('\n') if r.strip()]
                    if len(row) == 0:
                        pass
                    elif row[0] == 'MAC Address':
                        table[row[1]] = {row[0]: row[1]}
                        mac_address = row[1]
                    elif row[0] == 'IPv4 Address / Name':
                        table[mac_address].update({'IPv4 Address': row[1], 'Name': row[2][2:]})
                    elif row[0] == 'Connection Type':
                        connection_type = cache.get(row[1])
                        if connection_type:
                            pass
                        elif row[1][0:5] == 'Wi-Fi':
                            row_ = row[1].split('Type: ')
                            wifi = row_[0].split('\xa0 ')[1]
                            type_, name = row_[1].split('Name: ')
                            connection_type = {'Connection Type': {'Wi-Fi': wifi, 'type': type_, 'name': name}}
                        else:
                            connection_type = {'Connection Type': row[1]}
                        cache[row[1]] = connection_type
                        table[mac_address].update(connection_type)
                    else:
                        table[mac_address].update({row[0]: row[1]})
                return table

        class SystemInformation(Module):

            def get_info(self) -> dict:
                url = f'{self.bgw210.url}/cgi-bin//sysinfo.ha'
                self.bgw210.current_page = self.bgw210.session.get(url)
                table = {}
                rows = Tools.Parser.get_table_data(self.bgw210.current_page)
                for row in rows:
                    row = [r for r in row.text.split('\n') if r.strip()]
                    table[row[0]] = row[1]
                return table

        class AccessCode(Module):

            def use_default_access_code(self):
                pass

            def update_access_code(self, new_access_code: str):
                pass

        class RemoteAccess(Module):
            pass

        class RestartDevice(Module):

            def _navigate(self, method: str) -> None:
                url = f'{self.bgw210.url}/cgi-bin//sysinfo.ha'
                self.bgw210.current_page = self.bgw210.session.get(url)
                data = {'nonce': Tools.Parser.get_nonce(self.bgw210.current_page), method: method}
                self.bgw210.session.post(url=url, data=data)

            def restart(self) -> None:
                self._navigate(method='Restart')

            def cancel(self) -> None:
                self._navigate(method='Cancel')

    class Broadband:
        def __init__(self, bgw210: BGW210):
            self.Status = self.Status(bgw210)
            self.DeviceList = self.Configure(bgw210)

        class Status(Module):
            pass

            def get_status(self):
                pass

        class Configure(Module):

            def set(self, broadband_source_override: Literal[
                'Auto', 'DSL - Line 1', 'DSL - Line 2', 'DSL - Line 1 / Line 2', 'Ethernet'] = 'Auto',
                    base_mtu: int = 1500, ipv6_mtu: int = 1500):
                pass

    class HomeNetwork:
        def __init__(self, bgw210: BGW210):
            self.Status = self.Status(bgw210)
            self.Configure = self.Configure(bgw210)
            self.IPv6 = self.IPv6(bgw210)
            self.WiFi = self.WiFi(bgw210)
            self.MACFiltering = self.MACFiltering(bgw210)
            self.SubnetsDCHP = self.SubnetsDCHP(bgw210)
            self.IPAllocation = self.IPAllocation(bgw210)

        class Status(Module):
            def get_status(self):
                pass

        class Configure(Module):

            def ethernet(self, port_1: DropdownOptions.ethernet, port_2: DropdownOptions.ethernet,
                         port_3: DropdownOptions.ethernet,
                         port_4: DropdownOptions.ethernet):
                pass

            def mdi_x(self, port_1: DropdownOptions.auto_on_off, port_2: DropdownOptions.auto_on_off,
                      port_3: DropdownOptions.auto_on_off,
                      port_4: DropdownOptions.auto_on_off):
                pass

        class IPv6(Module):

            def set(self, ipv6: DropdownOptions.on_off, dhcp_v6: DropdownOptions.on_off,
                    dhcp_v6_prefix_delegation: DropdownOptions.on_off,
                    router_advertisement_mtu: int = 1500):
                pass

        class WiFi(Module):
            pass

        class MACFiltering(Module):
            pass

        class SubnetsDCHP(Module):
            pass

        class IPAllocation(Module):
            pass

    class Voice:
        def __init__(self, bgw210: BGW210):
            self.Status = self.Status(bgw210)
            self.LineDetails = self.LineDetails(bgw210)
            self.CallStatistics = self.CallStatistics(bgw210)

        class Status(Module):
            pass

        class LineDetails(Module):
            pass

        class CallStatistics(Module):
            pass

    class Firewall:
        def __init__(self, bgw210: BGW210):
            self.Status = self.Status(bgw210)
            self.PacketFilter = self.PacketFilter(bgw210)
            self.NATGaming = self.NATGaming(bgw210)
            self.PublicSubnetHosts = self.PublicSubnetHosts(bgw210)
            self.IPPassthrough = self.IPPassthrough(bgw210)
            self.FirewallAdvanced = self.FirewallAdvanced(bgw210)
            self.SecurityOptions = self.SecurityOptions(bgw210)

        class Status(Module):
            pass

        class PacketFilter(Module):
            pass

        class NATGaming(Module):
            pass

        class PublicSubnetHosts(Module):
            pass

        class IPPassthrough(Module):
            pass

        class FirewallAdvanced(Module):
            pass

        class SecurityOptions(Module):
            pass

    class Diagnostics:
        def __init__(self, bgw210: BGW210):
            self.Troubleshoot = self.Troubleshoot(bgw210)
            self.Logs = self.Logs(bgw210)
            self.Update = self.Update(bgw210)
            self.Resets = self.Resets(bgw210)
            self.Syslog = self.Syslog(bgw210)
            self.EventNotification = self.EventNotification(bgw210)
            self.NATTable = self.NATTable(bgw210)

        class Troubleshoot(Module):
            pass

        class SpeedTest(Module):
            pass

        class Logs(Module):
            pass

        class Update(Module):
            pass

        class Resets(Module):
            pass

        class Syslog(Module):
            pass

        class EventNotification(Module):
            pass

        class NATTable(Module):
            pass

    def login(self) -> Response:
        nonce = Tools.Parser.get_nonce(self.session.get(url=self.url, verify=False))
        data = {'nonce': nonce,
                'username': self.username,
                'password': ('*' * len(self.password)).encode('utf-8'),
                'hashpassword': md5((self.password + nonce).encode('utf-8')).hexdigest(),
                'Continue': 'Continue'}
        self.current_page = self.session.post(url=f'{self.url}/cgi-bin/login.ha', data=data)
        if BeautifulSoup(self.current_page.content, features="html.parser").find('title').text == 'Login':
            raise CredentialsError()
        return self.current_page

    def logout(self) -> Response:
        pass


router = BGW210()
router.Device.RestartDevice.restart()
