#!/usr/bin/python

import serial, time, io, datetime, random
from serial.tools.list_ports import comports

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.dates as mdates

#10 seconds of data
time_for_minrate= 10
#30 minutes of data
time_for_hourrate= 30*60

debug = True

update_cycle = 0.2 # Don't update more frequently than this

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

    if abs(m_den_sum) < 0.1:
        return 0.0

    return m_num_sum/m_den_sum

def tc_loop(n_tc, tc_data, tc_rate_min, tc_rate_hour):

    last_n_min = [[] for i in range(n_tc)]
    last_n_hour= [[] for i in range(n_tc)]
    time_n_min = []
    time_n_hour = []

    tc_port = None

    ports = comports()

    for port in ports:
        print port
    port = ports[0]
    print "Using ", port[0], " for TC readout"

    addresses = [b'A', b'E', b'I', b'M']

    #outfile_name = "tcdata_" + datetime.datetime.now().strftime("%Y%m%d%H%M.dat")
    #print "Writing to ", outfile_name
    #outfile = open(outfile_name, "w")

    print "Opening ", port, " for TC"

    if not debug:
        tc_port = serial.Serial(port[0], 9600, timeout= 5.0, parity=serial.PARITY_EVEN, xonxoff=0, rtscts=0, dsrdtr=0, bytesize=7, stopbits=1)

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
            time_n_min.append(time.time())
            time_n_hour.append(time.time())

            while time_n_min[-1] - time_n_min[0] > time_for_minrate:
                time_n_min.pop(0)

            while time_n_hour[-1] - time_n_hour[0] > time_for_hourrate:
                time_n_hour.pop(0)

            for i in range(n_tc):
                tc_data[i] = data[i] 
                last_n_min[i].append(data[i])
                last_n_hour[i].append(data[i])

                last_n_min[i]  = last_n_min[i][-len(time_n_min):]
                last_n_hour[i] = last_n_hour[i][-len(time_n_hour):]

                tc_rate_min[i]  = calc_rate(time_n_min, last_n_min[i])
                tc_rate_hour[i] = calc_rate(time_n_hour, last_n_hour[i])

        else:
            print "Malformed TC data"
            if not debug:
                tc_port.reset_input_buffer()

        if time.time() < start_time + update_cycle:
            time.sleep( update_cycle - (time.time()-start_time) )

