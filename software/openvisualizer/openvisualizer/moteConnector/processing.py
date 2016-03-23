__author__ = 'Mikhail Vilgelm'


from CompressionHelper import TestbedPacket, MeasurementPacket
import os
import matplotlib.pyplot as plt
import numpy as np
import sys


class LogProcessor:

    def __init__(self, filename):
        """
        Loads all packets into memory.
        :param filename:
        :return:
        """
        self.filename = filename  # we only store the filename
        self.packets = self.load_packets()

    def load_packets(self):
        """
        load all packets
        :return: packets list
        """
        packets = []
        for line in self.yield_line():

            lines = line.split('\t')
            line = lines[0]

            pkt = TestbedPacket.serialize_data(line)

            packets.append(pkt)

        return packets

    def yield_line(self):
        """
        Lazy file reading: to avoid loading full file into memory
        :return:
        """
        with open(self.filename, 'r') as f:
            for line in f:
                yield line

    def calculate_mean_delay(self):
        """
        :return: average delay
        """
        return np.mean(self.get_delays())


    def get_delays(self):
        """
        :return: delay list: delay for every packet in seconds
        """
        delay = []
        for line in self.yield_line():

            lines = line.split('\t')
            line = lines[0]

            pkt = TestbedPacket.serialize_data(line)

            d = pkt.get_delay()

            if d < 0:
                # shouldn't be the case...
                continue

            delay.append(d*15/1000)

        return delay

    def find_motes_in_action(self):
        """
        :return: set of motes sending or forwarding something, as seen from DAG root
        """
        motes = set()
        for line in self.yield_line():
            lines = line.split('\t')
            line = lines[0]

            if line == '[]':
                continue

            pkt = TestbedPacket.serialize_data(line)

            for v in pkt.hop_info:
                src = v['addr']
                if (src not in motes) and (src > 0) and (src <= 10):
                    motes.add(src)

        return motes

    def plot_delay(self, show=True):
        """

        :return:
        """
        plt.figure()
        plt.boxplot(self.get_delays())
        if show:
            plt.show()

    def get_avg_hops(self):
        """
        Calculate average number of hops
        :return:
        """

        pkt_hops = []
        for pkt in self.packets:

            if pkt.get_delay() < 0:
                print(pkt.asn_last)
                print(pkt.asn_first)
                # erroneous packet
                continue

            num_hops = 0
            for hop in pkt.hop_info:
                if hop['addr'] != 0:
                    num_hops += 1
            pkt_hops.append(num_hops)

        return np.mean(pkt_hops)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        exit("Usage: %s dumpfile" % sys.argv[0])

    # p = LogProcessor(os.getenv("HOME") + '/Projects/TSCH/github/dumps/tsch_dump_2016-03-23_14:45:49')

    p = LogProcessor(sys.argv[1])
    print(p.get_avg_hops())
