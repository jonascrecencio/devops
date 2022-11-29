from argparse import ArgumentParser
from netsnmp.walker import cbqosWalker
from prometheus_client import start_http_server
from sys import stderr, stdout
import time
import gevent

PROMETHEUS_CLIENT_PORT=9105
SNMP_WALK_INTERVAL=30

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
    start_http_server(PROMETHEUS_CLIENT_PORT)
    walker = cbqosWalker(args)
    metric = walker.define_metric()

    while True:        
        try:
            start = time.time()
            print('########### start: ', start)
            qos_if_rates = walker.walk_snmp()
            spawns = []
            for rate in qos_if_rates:
                print('###### for rate: ', rate)
                spawn = gevent.spawn(
                    walker.monit_rate,
                    rate=rate,
                    metric=metric
                )
                spawns.append(spawn)   
            stdout.flush()
            stderr.flush()
            end = time.time()
            print('################## end: ', end)
        except Exception:
            pass
        time_remaining = SNMP_WALK_INTERVAL - (end - start)
        wait = time_remaining if time_remaining > 0 else 0
        print('########## fim while, wait: ', wait)
        gevent.sleep(wait)