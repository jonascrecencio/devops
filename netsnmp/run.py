from argparse import ArgumentParser
from netsnmp.walker import cbqosWalker
from prometheus_client import start_http_server
from sys import stderr, stdout
import time
import gevent
import logging

PROMETHEUS_CLIENT_PORT=9105
SNMP_WALK_INTERVAL=30

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
LOGGER = logging.getLogger("netsnmp")

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
    LOGGER.info('Starting prometheus HTTP server...')
    start_http_server(PROMETHEUS_CLIENT_PORT)
    walker = cbqosWalker(args)
    metric = walker.define_metric()

    while True:        
        try:
            start = time.time()
            qos_if_rates = walker.walk_snmp()
            tasks = []
            for rate in qos_if_rates:
                spawn = gevent.spawn(
                    walker.monit_rate,
                    rate=rate,
                    metric=metric
                )
                tasks.append(spawn)
            stdout.flush()
            stderr.flush()
            end = time.time()
        except Exception:
            pass
        time_remaining = SNMP_WALK_INTERVAL - (end - start)
        wait = time_remaining if time_remaining > 0 else 0
        gevent.sleep(wait)