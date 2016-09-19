#!/usr/bin/python

import serial, time, io, datetime, random
from serial.tools.list_ports import comports

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.dates as mdates

n_for_ramp = 3

debug = False

update_cycle = 0.5 # Don't update more frequently than this

def calc_rate(times, points):
    n = len(times)

    if n < 2:
        return 0.0

    xavg = sum(times) /float(n)
    yavg = sum(points)/float(n)

    m_num_sum = 0.0
    m_den_sum = 0.0
    for i in range(n):
        m_num_sum += (times[i]-xavg)*(points[i]-yavg)
        m_den_sum += (times[i]-xavg)*(times[i]-xavg)

    return m_num_sum/m_den_sum

def tc_loop(n_tc, tc_data, tc_rate):

    last_n = [[] for i in range(n_tc)]
    time_n = []

    tc_port = None

    ports = comports()

    for port in ports:
        print port
    port = ports[0]

    addresses = [b'A', b'E', b'I', b'M']

    #outfile_name = "tcdata_" + datetime.datetime.now().strftime("%Y%m%d%H%M.dat")
    #print "Writing to ", outfile_name
    #outfile = open(outfile_name, "w")

    print "Opening ", port, " for TC"

    if not debug:
        tc_port = serial.Serial(port[0], 300, timeout= 5.0, parity=serial.PARITY_EVEN, xonxoff=0, rtscts=0, dsrdtr=0, bytesize=7, stopbits=1)

        tc_port.close()
        tc_port.open()

    while 1:
        data = []

        start_time = time.time()

        for addr in addresses:
#            print "Reading module ", addr
            if not debug:
                tc_port.write(b'$' + addr + b'RB\r')

            read_buff= []
            
            if not debug:
                read_buff.append(tc_port.read(53))
            else:
                read_buff.append("*20.0\r\0"*5)

            read_str = "".join(read_buff).replace('\0','').replace('*','').split('\r')

            for i in range(4):
                try:
                    data.append(float( read_str[i+1] ))
                    if debug:
                        data[-1] += random.uniform(-1.0, 1.0)

                except:
                    continue


        if len(data) == n_tc:
            time_n.append(time.time())
            if len(time_n) > n_for_ramp:
                time_n.pop(0)

            for i in range(n_tc):
                tc_data[i] = data[i] 
                last_n[i].append(data[i])
                if len(last_n[i]) > n_for_ramp:
                    last_n[i].pop(0)

                tc_rate[i] = calc_rate(time_n, last_n[i])

        else:
            print "Malformed TC data"
            if not debug:
                tc_port.reset_input_buffer()

        if time.time() < start_time + update_cycle:
            time.sleep( update_cycle - (time.time()-start_time) )

