import serial, time, io, datetime, math
from serial.tools.list_ports import comports

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.dates as mdates

from multiprocessing import Process, Pipe, Array


avg_time = 60.0# 1 minute moving average
pid_cycle_time = 0.001 # ms pid cycle
tc_tolerance = 5.0 # degC

debug = False

def set_ssr( port, chan, val ):
    if not debug:
        if chan == 0:
            port.dtr = val
        if chan == 1:
            port.rts = val


def pid_loop(T_setp, assigned_tc, T_ramp_state, T_ramp, tc_data, tc_rate, ssr_state, pidctrl_state, ssr_avg_power):

    n_to_average = avg_time/pid_cycle_time

    power_sum = [[] for i in range(len(ssr_state))]

    ssr_port = None
    if not debug:
        ports = comports()

        for port in ports:
            print port
        port = ports[2]

        print "Opening ", port, " for SSR control"

        ssr_port = serial.Serial(port[0], 300, timeout= 1, parity=serial.PARITY_NONE, xonxoff=0, rtscts=False, dsrdtr=False, bytesize=8, stopbits=1)

        ssr_port.close()
        ssr_port.open()

        ssr_port.dtr = False
        ssr_port.rts = False

    while 1:
        for ssr in range(len(ssr_state)):
            power_sum[ssr].append(ssr_state[ssr])
            if len(power_sum[ssr]) > n_to_average:
                power_sum[ssr].pop(0)
            
            ssr_avg_power[ssr] = sum(power_sum[ssr])/float(len(power_sum[ssr]))

            # Under control of PID
            if pidctrl_state[ssr]:
                if tc_data[assigned_tc[ssr]]  >  T_setp[ssr] + tc_tolerance: 
                    print "temp is high",  tc_data[assigned_tc[ssr]], T_setp[ssr]
                    # Think about turning off
                    if T_ramp_state[ssr]:
                        if tc_rate[assigned_tc[ssr]] < T_ramp[ssr]:
                            ssr_state[ssr] = True
                            # Turn on SSR
                            set_ssr(ssr_port, ssr, True)
                        else:
                            ssr_state[ssr] = False
                            # Turn off SSR
                            set_ssr(ssr_port, ssr, False)
                    else:
                        ssr_state[ssr] = False
                        # Turn off SSR
                        set_ssr(ssr_port, ssr, False)

                if tc_data[assigned_tc[ssr]]  <  T_setp[ssr] - tc_tolerance: 
                    print "temp is low",  tc_data[assigned_tc[ssr]], T_setp[ssr]
                    # Think about turning on
                    if T_ramp_state[ssr]:
                        if tc_rate[assigned_tc[ssr]] > T_ramp[ssr]:
                            ssr_state[ssr] = False
                            set_ssr(ssr_port, ssr, False)
                            # Turn off SSR
                        else:
                            ssr_state[ssr] = True 
                            set_ssr(ssr_port, ssr, True)
                            # Turn on SSR
                    else:
                        ssr_state[ssr] = True 
                        set_ssr(ssr_port, ssr, True)
                        # Turn on SSR
            # Not controled by PID, ssr state should be set *by* ssr_state
            else:
                if ssr_state[ssr]:
                    set_ssr(ssr_port, ssr, True)
                else:
                    set_ssr(ssr_port, ssr, False)

        time.sleep(pid_cycle_time)

