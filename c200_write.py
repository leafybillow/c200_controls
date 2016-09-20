#!/usr/bin/python

import serial, time, io, datetime, random
from serial.tools.list_ports import comports

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.dates as mdates

n_for_ramp = 3

debug = True

update_cycle = 5.0 # Don't update more frequently than this


def write(n_tc, n_ssr, ssr_avg_power, tc_data):


    outfile_name = "data/tcdata_" + datetime.datetime.now().strftime("%Y%m%d%H%M.dat")
    print "Writing to ", outfile_name
    outfile = open(outfile_name, "w")

    while 1:
        start_time = time.time()

        outfile.write(datetime.datetime.now().isoformat())
        outfile.write("\t")

        for ssr in range(n_ssr):
            outfile.write("%4.3f" % ssr_avg_power[ssr] )
            outfile.write("\t")


        for tc in range(n_tc):
            outfile.write("%4.1f" % tc_data[tc] )
            outfile.write("\t")

        outfile.write("\n")
        outfile.flush()

        if time.time() < start_time + update_cycle:
            time.sleep( update_cycle - (time.time()-start_time) )

