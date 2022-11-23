from argparse import ArgumentParser
from netsnmp.walker import cbqosWalker

def parse_args():
    parser = ArgumentParser(prog="net-snmp-cbqos", description="SNMP cbQos exporter")
    parser.add_argument(
        "-c", default="public", help="Community string"
    )
    parser.add_argument(
        "address", help="IP address or hostname to access (required)"
    )
    return parser.parse_args()

def run():
    args = parse_args()
    walker = cbqosWalker(args)
    walker.walk_interfaces()