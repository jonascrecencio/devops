from prometheus_client import Gauge, start_http_server
from easysnmp import Session

PROMETHEUS_CLIENT_PORT="9105"
CBQOS_OID="1.3.6.1.4.1.9.9.166"

#1.3.6.1.2.1.2.2.1.2 (nome)
#1.3.6.1.2.1.2.2.1.1 (index) o que interessa por baixo dos panos

class cbqosWalker():
    def __init__(self, args):
        self.address = args.address
        self.cbqos_oid = CBQOS_OID
        self.community = args.c

    def walk_interfaces(self):
        session = Session(hostname=self.address, community=self.community, version=2)
        teste1 = session.get('1.3.6.1.2.1.2.2.1.2')
        teste2= session.walk('1.3.6.1.2.1.2.2.1.2')
        teste3= session.bulkwalk('1.3.6.1.2.1.2.2.1.2')
        print(teste1)
        exit(0)
        device_conn = {
            'device_type': self.device,
            'host': self.address,
            'username': self.user,
            'password': self.password,
            'port': self.port,
        }
        try:
            net_connect = ConnectHandler(**device_conn)
        except NetMikoTimeoutException as e:
            LOGGER.error(e)
            raise SystemExit(1)

def init_metric():
    class_rate = Gauge(
        "cbQosCMPostPolicyBitRate",
        "The bit rate of the traffic after executing QoS policies.",
        ['interface', 'direction', 'class']
    )
    return class_rate

def run():
    prometheus_metric_labels = {
        "interface": "GigaEthernet 4",
        "direction": "in",
        "class": "ouro-pix",
    }
    start_http_server(PROMETHEUS_CLIENT_PORT)
    metric = init_metric()
    metric.labels(**prometheus_metric_labels).set(300000)
