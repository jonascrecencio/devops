from prometheus_client import Gauge, start_http_server
from easysnmp import Session

PROMETHEUS_CLIENT_PORT="9105"
INTERFACE_NAME_OID="1.3.6.1.2.1.2.2.1.2"
INTERFACE_INDEX_OID="1.3.6.1.2.1.2.2.1.1"
INTERFACE_CBQOS_INDEX="1.3.6.1.4.1.9.9.166.1.1.1.1.4"
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
        if_indexes = session.bulkwalk(INTERFACE_INDEX_OID)
        if_names = session.bulkwalk(INTERFACE_NAME_OID)
        interfaces = { if_indexes[i].value : if_names[i].value for i in range(len(if_indexes))}
        print(interfaces)
        exit(0)
        return interfaces

        # print(teste1)
        # exit(0)
        # device_conn = {
        #     'device_type': self.device,
        #     'host': self.address,
        #     'username': self.user,
        #     'password': self.password,
        #     'port': self.port,
        # }
        # try:
        #     net_connect = ConnectHandler(**device_conn)
        # except NetMikoTimeoutException as e:
        #     LOGGER.error(e)
        #     raise SystemExit(1)

    def check_qos_policy(self, interfaces):
        session = Session(hostname=self.address, community=self.community, version=2)
        if_cbqos_index = session.bulkwalk(INTERFACE_CBQOS_INDEX)
        print(if_cbqos_index)
        exit(0)
        
# def init_metric():
#     class_rate = Gauge(
#         "cbQosCMPostPolicyBitRate",
#         "The bit rate of the traffic after executing QoS policies.",
#         ['interface', 'direction', 'class']
#     )
#     return class_rate

# def run():
#     prometheus_metric_labels = {
#         "interface": "GigaEthernet 4",
#         "direction": "in",
#         "class": "ouro-pix",
#     }
#     start_http_server(PROMETHEUS_CLIENT_PORT)
#     metric = init_metric()
#     metric.labels(**prometheus_metric_labels).set(300000)
