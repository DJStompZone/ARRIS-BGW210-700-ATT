from __future__ import annotations

from hashlib import md5
from typing import Literal

from bs4 import BeautifulSoup
from requests import Response, Session
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from .Menus import Dropdown
from .tools import Tools

disable_warnings(InsecureRequestWarning)


class Module:
    def __init__(self, bgw210: BGW210):
        self.bgw210 = bgw210


class BGW210:
    def __init__(self, ip: str = None, port: int = None, username: str = None, password: str = None) -> None:
        self.session = Session()
        self.current_page = Response()
        url = f'{Tools.Network.resolve_secure()}{ip}:{port}'
        if not all([ip, port, username, password]):
            config = Tools.Network.get_credentials()
            url, username, password = [config.url, config.username, config.password]
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

            def _restart(self, device: Literal['crestart', 'wrestart', 'vrestart'], url_query: int,
                         method: str) -> None:
                url = f'{self.bgw210.url}/cgi-bin/home.ha'
                data = {'nonce': Tools.Parser.get_nonce(self.bgw210.session.get(url)), method: 'Restart'}
                self.bgw210.current_page = self.bgw210.session.post(
                    url=f'{self.bgw210.url}/cgi-bin/{device}.ha?{url_query}', data=data)

            def more_info(self) -> dict:
                return self.bgw210.Device.SystemInformation.get_info()

            def restart_broadband(self) -> None:
                self._restart(device='crestart', url_query=1, method='Broadband')

            def restart_2_4ghz_wifi(self) -> None:
                self._restart(device='wrestart', url_query=1, method='WRestart1')

            def restart_5ghz_wifi(self) -> None:
                self._restart(device='wrestart', url_query=2, method='WRestart1')

            def restart_line_1(self) -> None:
                self._restart(device='vrestart', url_query=1, method='VRestart1')

            def restart_line_2(self) -> None:
                self._restart(device='vrestart', url_query=2, method='VRestart2')

            def devices(self) -> dict:
                return self.bgw210.Device.DeviceList.get_devices()

        class DeviceList(Module):

            def clear_and_rescan_for_devices(self) -> dict:
                url = f'{self.bgw210.url}/cgi-bin/devices.ha'
                data = {'nonce': Tools.Parser.get_nonce(self.bgw210.session.get(url)),
                        'Clear': 'Clear and Rescan for Devices'}
                self.bgw210.current_page = self.bgw210.session.post(url=url, data=data)
                return self.get_devices(False)

            def get_devices(self, refresh: bool = True) -> dict:
                mac_address = ''
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
                url = f'{self.bgw210.url}/cgi-bin/sysinfo.ha'
                data = {'nonce': Tools.Parser.get_nonce(self.bgw210.session.get(url)), method: method}
                self.bgw210.current_page = self.bgw210.session.post(url=url, data=data)

            def restart(self) -> None:
                self._navigate(method='Restart')

            def cancel(self) -> None:
                self._navigate(method='Cancel')

    class Broadband:
        def __init__(self, bgw210: BGW210):
            self.Status = self.Status(bgw210)
            self.DeviceList = self.Configure(bgw210)

        class Status(Module):

            def get_status(self) -> dict:
                table = {}
                columns = []
                self.bgw210.current_page = self.bgw210.session.get(f'{self.bgw210.url}/cgi-bin/broadbandstatistics.ha')
                rows = Tools.Parser.get_table_data(self.bgw210.current_page)
                sections = ['Primary Broadband', 'DSL Status', 'Timed Statistics', 'Aggregated Information', 'IPv6',
                            'IPv4 Statistics', 'IPv6 Statistics']
                section = sections.pop(0)
                table[section] = {}
                for row in rows:
                    row = [r for r in row.text.split('\n') if r.strip()]
                    if row == ['Line 1', 'Line 2'] or (len(row) > 0 and row[0] == '\xa015 Min'):
                        section = sections.pop(0)
                        table[section] = {}
                        if row[0] == '\xa015 Min':
                            columns = row
                            columns[0] = '15 Min'
                        continue
                    if len(row) == 2:
                        if row[0] in {'Bonded Downstream Rate', 'Status', 'Transmit Packets'}:
                            section = sections.pop(0)
                            table[section] = {}
                        try:
                            table[section][row[0]] = int(row[1].strip())
                        except ValueError:
                            table[section][row[0]] = row[1].strip()
                    elif len(row) == 3:
                        try:
                            table[section][row[0]] = {'Line 1': int(row[1]), 'Line 2': int(row[2])}
                        except ValueError:
                            table[section][row[0]] = {'Line 1': row[1], 'Line 2': row[2]}
                    elif len(row) == 5:
                        table[section][row[0]] = {'Line 1 Downstream': float(row[1].strip()),
                                                  'Line 1 Upstream': float(row[2].strip()),
                                                  'Line 2 Downstream': float(row[3].strip()),
                                                  'Line 2 Upstream': float(row[4].strip())}
                    elif len(row) == 6:
                        table[section][row[0]] = dict(map(lambda key, value: (key, int(value)), columns, row[1:]))
                return table

            def clear_statistics(self) -> None:
                url = f'{self.bgw210.url}/cgi-bin/broadbandstatistics.ha'
                data = {'nonce': Tools.Parser.get_nonce(self.bgw210.session.get(url)), 'Clear': 'Clear Statistics'}
                self.bgw210.current_page = self.bgw210.session.post(url=url, data=data)

        class Configure(Module):

            def set(self, broadband_source_override: Literal['auto', 'line1', 'line2', 'dslauto', 'ethernet'] = 'auto',
                    base_mtu: int = 1500, ipv6_mtu: int = None) -> None:
                url = f'{self.bgw210.url}/cgi-bin/broadbandconfig.ha'
                data = {'nonce': Tools.Parser.get_nonce(self.bgw210.session.get(url)),
                        'source': broadband_source_override, 'MTUW': base_mtu, 'Save': 'Save'}
                if ipv6_mtu:
                    data.update({'MTU6': ipv6_mtu})
                self.bgw210.current_page = self.bgw210.session.post(url=url, data=data)

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

            def set(self, ethernet_port_1: Dropdown.ethernet = 'auto', ethernet_port_2: Dropdown.ethernet = 'auto',
                    ethernet_port_3: Dropdown.ethernet = 'auto', ethernet_port_4: Dropdown.ethernet = 'auto',
                    mdi_x_port_1: Dropdown.auto_on_off = 'auto', mdi_x_port_2: Dropdown.auto_on_off = 'auto',
                    mdi_x_port_3: Dropdown.auto_on_off = 'auto', mdi_x_port_4: Dropdown.auto_on_off = 'auto'):
                url = f'{self.bgw210.url}/cgi-bin/etherlan.ha'
                data = {'nonce': Tools.Parser.get_nonce(self.bgw210.session.get(url)),
                        'enet1_port1_media': ethernet_port_1, 'enet2_port2_media': ethernet_port_2,
                        'enet3_port3_media': ethernet_port_3, 'enet4_port4_media': ethernet_port_4,
                        'enet1_port1_mdix': mdi_x_port_1, 'enet2_port2_mdix': mdi_x_port_2,
                        'enet3_port3_mdix': mdi_x_port_3, 'enet4_port4_mdix': mdi_x_port_4,
                        'Save': 'Save'}
                self.bgw210.current_page = self.bgw210.session.post(url=url, data=data)

        class IPv6(Module):

            def set(self, ipv6: Dropdown.on_off = 'on', dhcp_v6: Dropdown.on_off = 'on',
                    dhcp_v6_prefix_delegation: Dropdown.on_off = 'on', router_advertisement_mtu: int = None):
                url = f'{self.bgw210.url}/cgi-bin/ip6lan.ha'
                data = {'nonce': Tools.Parser.get_nonce(self.bgw210.session.get(url)),
                        'ipv6lan': ipv6, 'dhcpv6': dhcp_v6, 'dhcpv6pd': dhcp_v6_prefix_delegation, 'Save': 'Save'}
                if router_advertisement_mtu:
                    data.update({'MTU6': router_advertisement_mtu})
                self.bgw210.current_page = self.bgw210.session.post(url=url, data=data)

        class WiFi(Module):
            def get_settings(self) -> dict:
                self.bgw210.current_page = self.bgw210.session.get(f'{self.bgw210.url}/cgi-bin/wconfig_unified.ha')
                return Tools.Parser.parse_fields(self.bgw210.current_page)

            def advanced_options(self) -> dict:
                self.bgw210.current_page = self.bgw210.session.get(f'{self.bgw210.url}/cgi-bin/wconfig.ha')
                return Tools.Parser.parse_fields(self.bgw210.current_page)

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
                'password': self.password,
                'Continue': 'Continue'}
        self.current_page = self.session.post(url=f'{self.url}/cgi-bin/login.ha', data=data)
        if BeautifulSoup(self.current_page.content, features="html.parser").find('title').text == 'Login':
            raise Exception('CredentialsError - Bad username/password')
        return self.current_page

    def logout(self) -> Response:
        pass


router = BGW210()
router.HomeNetwork.WiFi.advanced_options()
