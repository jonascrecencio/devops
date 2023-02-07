from prometheus_client import Gauge
from easysnmp import Session
import logging

INTERFACE_NAME_OID="1.3.6.1.2.1.2.2.1.2"
INTERFACE_CBQOS_INDEX="1.3.6.1.4.1.9.9.166.1.1.1.1.4"
CBQOS_POLICY_DIRECTION="1.3.6.1.4.1.9.9.166.1.1.1.1.3"
CBQOS_CLASSES="1.3.6.1.4.1.9.9.166.1.7.1.1.1"
CBQOS_OBJECTS="1.3.6.1.4.1.9.9.166.1.5.1.1.2"
CBQOS_TYPE="1.3.6.1.4.1.9.9.166.1.5.1.1.3"
CBQOS_BIT_RATE="1.3.6.1.4.1.9.9.166.1.15.1.1.11"
CBQOS_POLICY_NAME="1.3.6.1.4.1.9.9.166.1.6.1.1.1"

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
LOGGER = logging.getLogger("netsnmp")

class cbqosWalker():
    def __init__(self, args):
        self.address = args.address
        self.community = args.c

    def walk_snmp(self):
        if_rates = []
        for host in self.address:
            try:
                session = Session(hostname=host, community=self.community, version=2)
                if_names = session.bulkwalk(INTERFACE_NAME_OID)
                if_cbqos = session.bulkwalk(INTERFACE_CBQOS_INDEX)
                cbqos_pol_direction = session.bulkwalk(CBQOS_POLICY_DIRECTION)
                cbqos_classes = session.bulkwalk(CBQOS_CLASSES)
                cbqos_objects = session.bulkwalk(CBQOS_OBJECTS)
                cbqos_type = session.bulkwalk(CBQOS_TYPE)
                cbqos_bit_rate = session.bulkwalk(CBQOS_BIT_RATE)
                cbqos_pol_name = session.bulkwalk(CBQOS_POLICY_DIRECTION)
            except:
                LOGGER.error('Failed to snmp bulkwalk host %s!', host)
                continue

            for i in range(len(cbqos_type)):
                if cbqos_type[i].value != "2":
                    continue
                policy = cbqos_objects[i].oid.split(".")[-2]
                policy_config = next(x.value for x in cbqos_objects if x.oid.split(".")[-1] == policy and x.oid.split(".")[-2] == policy)
                policy_name = next(x.value for x in cbqos_pol_name if x.oid.split(".")[-1] == policy_config)
                rate = next(x.value for x in cbqos_bit_rate if x.oid.split(".")[-1] == cbqos_objects[i].oid.split(".")[-1])
                direction = next(x.value for x in cbqos_pol_direction if x.oid.split(".")[-1] == policy)
                cbqos_class = next(x.value for x in cbqos_classes if x.oid.split(".")[-1] == cbqos_objects[i].value)
                if_index = next(x.value for x in if_cbqos if x.oid.split(".")[-1] == policy)
                interface = if_names[int(if_index) - 1].value
                if_rates.append({
                    "device" : host,
                    "interface" : interface,
                    "direction" : direction,
                    "qos_class" : cbqos_class,
                    "policy" : policy,
                    "policy_name": policy_name,
                    "rate" : rate
                })
        return if_rates

    def define_metric(self):
        metric = Gauge(
            "cb_qos_cm_post_policy_bit_rate",
            "The bit rate of the traffic after executing QoS policies.",
            ['device', 'interface', 'direction', 'qos_class', 'policy', 'policy_name']
        )
        return metric

    def monit_rate(self, rate, metric):
        prometheus_metric_labels = {
            "device" : rate['device'],
            "interface" : rate['interface'],
            "direction" : rate['direction'],
            "qos_class" : rate['qos_class'],
            "policy" : rate['policy'],
            "policy_name" : rate['policy_name']
        }
        try:
            metric.labels(**prometheus_metric_labels).set(rate['rate'])
            LOGGER.info(
                "Metric update: device = %s, intefacer = %s, policy = %s, policy_name = %s, direction = %s, class =  %s, rate = %s",
                rate['device'],
                rate['interface'],
                rate['policy'],
                rate['policy_name'],
                rate['direction'],
                rate['qos_class'],
                rate['rate']
            )
        except:
            LOGGER.error("Unable to update prometheus metric!")