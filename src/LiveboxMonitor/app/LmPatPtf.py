### Livebox Monitor PAT/PTF rules handling constants ###

from enum import IntEnum

IPV6_SOURCE_PORT_WORKING = False        # SourcePort is available in the API but not working, at least for a LB5

RULE_TYPE_IPv4 = 'IPv4'
RULE_TYPE_IPv6 = 'IPv6'
RULE_TYPE_UPnP = 'UPnP'
RULE_PAT_TYPES = [RULE_TYPE_IPv4, RULE_TYPE_IPv6, RULE_TYPE_UPnP]
RULE_PTF_TYPES = [RULE_TYPE_IPv4, RULE_TYPE_IPv6]

# Protocols - https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml
# Numbers
class Protocols(IntEnum):
    ICMP = 1
    TCP = 6
    UDP = 17
    GRE = 47
    ESP = 50
    AH = 51
    ICMPv6 = 58

# Names
PROTOCOL_NAMES = {
    '1':    'ICMP',
    '2':    'IGMP',
    '3':    'GGP',
    '4':    'IPv4',
    '5':    'ST',
    '6':    'TCP',
    '7':    'CBT',
    '8':    'EGP',
    '9':    'IGP',
    '10':   'BBN',
    '11':   'NVP',
    '12':   'PUP',
    '17':   'UDP',
    '18':   'MUX',
    '20':   'HMP',
    '27':   'RDP',
    '33':   'DCCP',
    '37':   'DDP',
    '40':   'IL',
    '41':   'IPv6',
    '46':   'RSVP',
    '47':   'GRE',
    '48':   'DSR',
    '49':   'BNA',
    '50':   'ESP',
    '51':   'AH',
    '58':   'ICMPv6',
    '75':   'PVP',
    '84':   'IPTM',
    '86':   'DGP',
    '87':   'TCF',
    '88':   'EIGRP',
    '89':   'OSPF',
    '92':   'MTP'
}
