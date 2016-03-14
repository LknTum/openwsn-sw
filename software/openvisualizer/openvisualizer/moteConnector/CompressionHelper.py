__author__ = 'Mikhail Vilgelm'

import pickle
import pprint


class TestbedPacket:

    @classmethod
    def serialize_data(cls, data, format='SMARTGRID'):
        if format == 'SMARTGRID':
            return MeasurementPacket(asn_first=int(data[0]), asn_last=int(data[1]),
                                     src_addr=int(data[2]), seqN=int(data[3]),
                                     num_hops=int(data[4]), hop_info=data[5])
        elif format == 'AIRCRAFT':
            return StringPacket(data)


class StringPacket:

    def __init__(self, data):
        self.data = data

    def dump_compressed(self):
        return self.data


class MeasurementPacket:
    """
    Packet sniffed from Smartgrid measurements
    """

    def __init__(self, **kwargs):
        self.asn_first = kwargs['asn_first']
        self.asn_last = kwargs['asn_last']
        self.src_addr = kwargs['src_addr']
        self.seqN = kwargs['seqN']
        num_hops = kwargs['num_hops']
        self.hop_info = []
        for i in range(kwargs['num_hops']):
            self.hop_info.append(kwargs['hop_info'])


    def dump_as_ipv6(self):
        """
        Recover full ipv6 packet from a compressed entry
        :return:
        """
        # TODO
        # recover ipv6 header
        # recover udp header
        pass

    def dump_compressed(self):
        return pickle.dumps(self)



if __name__=='__main__':
    '''
    Testing
    '''
    test = ['0', '1', '2', '0', '1', '2']

    pkt = TestbedPacket.serialize_data(test)

    pkt_serialized = pkt.dump_compressed()
    print(pkt_serialized)
    pkt_recovered = pickle.loads(pkt_serialized)
    print(pkt_recovered.asn_first)
    print(pkt_recovered.src_addr)
