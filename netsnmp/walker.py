from prometheus_client import Gauge, start_http_server
from easysnmp import Session

PROMETHEUS_CLIENT_PORT="9105"
INTERFACE_NAME_OID="1.3.6.1.2.1.2.2.1.2"
INTERFACE_INDEX_OID="1.3.6.1.2.1.2.2.1.1"
INTERFACE_CBQOS_INDEX="1.3.6.1.4.1.9.9.166.1.1.1.1.4"
CBQOS_OID="1.3.6.1.4.1.9.9.166"
CBQOS_POLICY_DIRECTION="1.3.6.1.4.1.9.9.166.1.1.1.1.3"
CBQOS_CLASSES="1.3.6.1.4.1.9.9.166.1.7.1.1.1"
CBQOS_OBJECTS="1.3.6.1.4.1.9.9.166.1.5.1.1.2"
CBQOS_TYPE="1.3.6.1.4.1.9.9.166.1.5.1.1.3"
CBQOS_BIT_RATE="1.3.6.1.4.1.9.9.166.1.15.1.1.11"

#1.3.6.1.2.1.2.2.1.2 (nome)
#1.3.6.1.2.1.2.2.1.1 (index) o que interessa por baixo dos panos

class cbqosWalker():
    def __init__(self, args):
        self.address = args.address
        self.cbqos_oid = CBQOS_OID
        self.community = args.c

    def walk_snmp(self):
        session = Session(hostname=self.address, community=self.community, version=2)
        if_indexes = session.bulkwalk(INTERFACE_INDEX_OID)
        if_names = session.bulkwalk(INTERFACE_NAME_OID)
        if_cbqos = session.bulkwalk(INTERFACE_CBQOS_INDEX)
        cbqos_pol_direction = session.bulkwalk(CBQOS_POLICY_DIRECTION)
        cbqos_classes = session.bulkwalk(CBQOS_CLASSES)
        cbqos_objects = session.bulkwalk(CBQOS_OBJECTS)
        cbqos_type = session.bulkwalk(CBQOS_TYPE)
        cbqos_bit_rate = session.bulkwalk(CBQOS_BIT_RATE)

        if_rates = []
        for i in range(len(cbqos_type)):
            if cbqos_type[i].value != 2:
                pass
            policy = cbqos_objects[i].oid.split(".")[-2]
            rate = next(x.value for x in cbqos_bit_rate if [ x.oid.split(".")[-1] == cbqos_objects[i].oid.split(".")[-1] ])
            direction = next(x.value for x in cbqos_pol_direction if [ x.oid.split(".")[-1] == policy ])
            cbqos_class = next(x.value for x in cbqos_classes if [ x.oid.split(".")[-1] == cbqos_objects[i].value ])
            if_index = next(x.value for x in if_cbqos if [ x.oid.split(".")[-1] == policy ])
            interface = if_names[int(if_index) - 1].value
            if_rates.append({
                "rate" : rate,
                "policy" : policy,
                "direction" : direction,
                "class" : cbqos_class,
                "interface" : interface
            })
        print(if_rates)
        exit(0)
        return if_rates

    def walk_interfaces(self):
        session = Session(hostname=self.address, community=self.community, version=2)
        if_indexes = session.bulkwalk(INTERFACE_INDEX_OID)
        if_names = session.bulkwalk(INTERFACE_NAME_OID)
        interfaces = []
        for i in range(len(if_indexes)):
            interfaces.append({
                "Index" : if_indexes[i].value,
                "Name" : if_names[i].value
            })
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
        if_cbqos = session.bulkwalk(INTERFACE_CBQOS_INDEX)
        if_cbqos_indexes =[]
        for i in range(len(if_cbqos)):
            if_cbqos_indexes.append({
                "Index" : if_cbqos[i].value,
                "Policy" : if_cbqos[i].oid
            })

        #qos_interfaces = [i for i in interfaces if i["Index"] in ]
        #print(if_cbqos_index)
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
