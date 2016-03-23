__author__ = 'Mikhail Vilgelm'


from CompressionHelper import TestbedPacket, MeasurementPacket
import os
import matplotlib.pyplot as plt


class LogProcessor:

    def __init__(self, filename):
        self.filename = filename


    def calculate_mean_delay(self):
        """

        :return: average delay
        """
        delay = []
        for line in self.yield_line():

            lines = line.split('\t')
            line = lines[0]

            pkt = TestbedPacket.serialize_data(line)

            # print(pkt.hop_info[0])

            if pkt.src_addr != pkt.hop_info[0]['addr']:
                # not our packet -- probably RPL
                continue

            d = pkt.asn_last - pkt.asn_first
            if d < 0:
                continue

            delay.append(d*15/1000)

        plt.figure()
        plt.boxplot(delay)
        plt.show()

        return np.mean(delay)

    def calculate_network_size(self):
        """
        :return:
        """

        hops = set()
        for line in self.yield_line():
            lines = line.split('\t')
            line = lines[0]

            if line == '[]':
                continue

            pkt = TestbedPacket.serialize_data(line)

            for v in pkt.hop_info:
                src = v['addr']
                if (src not in hops) and (src > 0) and (src <= 10):
                    hops.add(src)

        return hops



    def yield_line(self):
        """
        Lazy file reading
        :return:
        """
        with open(self.filename, 'r') as f:
            for line in f:
                yield line


if __name__ == '__main__':
    p = LogProcessor(os.getenv("HOME") + '/Projects/TSCH/github/dumps/tsch_dump_2016-03-23_14:45:49')

    hops = p.calculate_network_size()

    print(hops)