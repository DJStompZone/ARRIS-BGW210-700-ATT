from typing import Literal


class Dropdown:
    ethernet = Literal[
        'Auto',
        '100M full duplex',
        '100M half duplex',
        '10M full duplex',
        '10M half duplex',
        '1G full duplex',
        '1G full duplex']
    on_off = Literal['Off', 'On']
    auto_on_off = Literal['Auto', 'Off', 'On']
