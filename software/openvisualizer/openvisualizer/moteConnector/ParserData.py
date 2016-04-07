# Copyright (c) 2010-2013, Regents of the University of California.
# All rights reserved.
#
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('ParserData')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())

import struct
import datetime
import os

from pydispatch import dispatcher

from ParserException import ParserException
import Parser


# here are LKN-specific parameters for the dumps
gl_dump_path = os.getenv("HOME") + '/Projects/TSCH/github/dumps/'

class ParserData(Parser.Parser):

    HEADER_LENGTH  = 2
    MSPERSLOT      = 15 #ms per slot.

    IPHC_SAM       = 4
    IPHC_DAM       = 0

    # @lkn{mvilgelm} three flags indicating whether LKN-style compression is enabled
    ENABLE_COMPRESSION = True
    ENABLE_LOG_COMPRESSED_PKTS = True
    ENABLE_DISPLAY_PKTS = True


    def __init__(self):

        # log
        log.info("create instance")

        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)

        self._asn= ['asn_4',                     # B
          'asn_2_3',                   # H
          'asn_0_1',                   # H
         ]

        # @lkn{mvilgelm} if compression is enabled, separate log file is created
        if self.ENABLE_LOG_COMPRESSED_PKTS:
            self.zero_time = datetime.datetime.now()
            self.f_dump_name = gl_dump_path + 'tsch_dump_' + \
                               str(self.zero_time).split('.')[0].replace(' ', '_')
            f_dump = open(self.f_dump_name, 'w+')
            f_dump.close()



    #======================== public ==========================================

    def parseInput(self,input):

        # log
        if log.isEnabledFor(logging.DEBUG):
            log.info("received data {0}".format(input))

        # ensure input not short longer than header
        self._checkLength(input)

        headerBytes = input[:2]
        # asn comes in the next 5bytes.

        # @lkn{mvilgelm} Here comes parsing "compressed" packets: if compression is enabled, next byte will indicate
        # whether the packet is compressed or not. Separate log file is produced for this packet

        is_compressed = False

        source = []

        if self.ENABLE_DISPLAY_PKTS:
            print(input[3:])

        if self.ENABLE_COMPRESSION:
            if int(input[2]) == 1:
                is_compressed = True
            input.pop(2)
            if self.ENABLE_LOG_COMPRESSED_PKTS:
                f_dump = open(self.f_dump_name, 'a')
                # TODO recover full ipv6 packet
                # pkt = TestbedPacket.serialize_data(str(input[2:]), format='SMARTGRID')
                f_dump.write(str(input[2:]) + '\t' + str(datetime.datetime.now()-self.zero_time).encode('utf-8') + '\n')
                f_dump.close()

            source = input[2]

        if not is_compressed:
            asnbytes=input[2:7]
            (self._asn) = struct.unpack('<BHH',''.join([chr(c) for c in asnbytes]))

            #source and destination of the message
            dest = input[7:15]

            #source is elided!!! so it is not there.. check that.
            source = input[15:23]

            if log.isEnabledFor(logging.DEBUG):
                a="".join(hex(c) for c in dest)
                log.debug("destination address of the packet is {0} ".format(a))

            if log.isEnabledFor(logging.DEBUG):
                a="".join(hex(c) for c in source)
                log.debug("source address (just previous hop) of the packet is {0} ".format(a))

            # remove asn src and dest and mote id at the beginning.
            # this is a hack for latency measurements... TODO, move latency to an app listening on the corresponding port.
            # inject end_asn into the packet as well
            input = input[23:]

            if log.isEnabledFor(logging.DEBUG):
                log.debug("packet without source,dest and asn {0}".format(input))

            # when the packet goes to internet it comes with the asn at the beginning as timestamp.

            # cross layer trick here. capture UDP packet from udpLatency and get ASN to compute latency.
            # then notify a latency component that will plot that information.
            # port 61001==0xee,0x49
            if (len(input) >37):
               if (input[36]==238 and input[37]==73):
                # udp port 61001 for udplatency app.
                   aux      = input[len(input)-5:]               # last 5 bytes of the packet are the ASN in the UDP latency packet
                   diff     = self._asndiference(aux,asnbytes)   # calculate difference
                   timeinus = diff*self.MSPERSLOT                # compute time in ms
                   SN       = input[len(input)-23:len(input)-21] # SN sent by mote
                   parent   = input[len(input)-21:len(input)-13] # the parent node is the first element (used to know topology)
                   node     = input[len(input)-13:len(input)-5]  # the node address

                   if (timeinus<0xFFFF):
                   # notify latency manager component. only if a valid value
                      dispatcher.send(
                         sender        = 'parserData',
                         signal        = 'latency',
                         data          = (node,timeinus,parent,SN),
                      )
                   else:
                       # this usually happens when the serial port framing is not correct and more than one message is parsed at the same time. this will be solved with HDLC framing.
                       print "Wrong latency computation {0} = {1} mS".format(str(node),timeinus)
                       print ",".join(hex(c) for c in input)
                       log.warning("Wrong latency computation {0} = {1} mS".format(str(node),timeinus))
                       pass
                   # in case we want to send the computed time to internet..
                   # computed=struct.pack('<H', timeinus)#to be appended to the pkt
                   # for x in computed:
                       #input.append(x)
               else:
                   # no udplatency
                   # print input
                   pass
            else:
               pass

            eventType='data'
            # notify a tuple including source as one hop away nodes elide SRC address as can be inferred from MAC layer header
            return (eventType,(source,input))

        eventType='lkndata'
        return (eventType,(source,input))

 #======================== private =========================================

    def _asndiference(self,init,end):

       asninit = struct.unpack('<HHB',''.join([chr(c) for c in init]))
       asnend  = struct.unpack('<HHB',''.join([chr(c) for c in end]))
       if (asnend[2] != asninit[2]): #'byte4'
          return 0xFFFFFFFF
       else:
           pass

       diff = 0;
       if (asnend[1] == asninit[1]):#'bytes2and3'
          return asnend[0]-asninit[0]#'bytes0and1'
       else:
          if (asnend[1]-asninit[1]==1):##'bytes2and3'              diff  = asnend[0]#'bytes0and1'
              diff += 0xffff-asninit[0]#'bytes0and1'
              diff += 1;
          else:
              diff = 0xFFFFFFFF

       return diff