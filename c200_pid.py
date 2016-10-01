import serial, time, io, datetime, math, os
from serial.tools.list_ports import comports

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.dates as mdates

from multiprocessing import Process, Pipe, Array


avg_time = 30.0# 1 minute moving average
pid_cycle_time = 0.001 # ms pid cycle

debug = True

hard_temp_limit = 240.0
hard_rate_limit = 5.0/60.0 # 5 deg/min

def set_ssr( port, chan, val ):
    if not debug:
        if chan == 0:
            port.dtr = val
        if chan == 1:
            port.rts = val


def pid_loop(T_setp, prop_setp, assigned_tc, T_ramp_state, T_ramp, tc_data, tc_rate_min, tc_rate_hour, ssr_off, ssr_state, ssr_rb, pidctrl_state, ssr_avg_power):

    n_to_average = avg_time/pid_cycle_time

    power_sum = [[] for i in range(len(ssr_state))]

    ssr_port = None
    if not debug:
        ports = comports()

        for port in ports:
            print port
        port = ports[1]
        print "Opening ", port, " for SSR control"

        ssr_port = serial.Serial(port[0], 9600, timeout= 1, parity=serial.PARITY_NONE, xonxoff=0, rtscts=False, dsrdtr=False, bytesize=8, stopbits=1)

        ssr_port.close()
        ssr_port.open()

        ssr_port.dtr = False
        ssr_port.rts = False

    all_off = False
    while 1:
        for tcval in tc_data:
            if tcval > hard_temp_limit and not all_off:
                # Hit emergency limit
                all_off = True
                # Push to slack
                os.system("curl -X POST -H \'Content-type: application/json\' --data \'{\"channel\": \"#c200\", \"text\":\"C200 shutting down!  Temperature saftey threshold met\"}\' https://hooks.slack.com/services/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")


        for ssr in range(len(ssr_state)):
            if all_off:
                ssr_off[ssr] = True

            power_sum[ssr].append(ssr_state[ssr])
            if len(power_sum[ssr]) > n_to_average:
                power_sum[ssr].pop(0)
            
            ssr_avg_power[ssr] = sum(power_sum[ssr])/float(len(power_sum[ssr]))

            # Under control of PID
            if pidctrl_state[ssr]:
                calc_setpoint = 0.0

                diff = tc_data[assigned_tc[ssr]] -  T_setp[ssr];

                # Temp is low
                if diff < 0:
                    calc_setpoint = -prop_setp[ssr]*diff

                # Ramp rate is too high
                if T_ramp_state[ssr]:
                    ramp_x = 0.0
                    if abs(T_ramp[ssr]) > 1e-2:
                        ramp_x = 1.0 - (T_ramp[ssr] - tc_rate_min[assigned_tc[ssr]])/T_ramp[ssr]
                    else:
                        ramp_x = 0.0

                    if T_ramp[ssr] > 0.0:
                        if ramp_x > 1.0:
                            calc_setpoint = 0.0
                        else:
                            if ramp_x > 0.75:
                                calc_setpoint *= (ramp_x-0.75)/0.25

                    if T_ramp[ssr] < 0.0:
                        if ramp_x > 1.0:
                            calc_setpoint = 1.0
                        else:
                            if ramp_x > 0.75:
                                calc_setpoint *= (ramp_x-0.75)/0.25


                ramp_hard_x  = 1.0 - (hard_rate_limit- tc_rate_min[assigned_tc[ssr]])/hard_rate_limit
                if ramp_hard_x > 1.0:
                    calc_setpoint = 0.0
                else:
                    if ramp_hard_x > 0.75:
                        calc_setpoint *= (ramp_hard_x-0.75)/0.25


                ssr_rb[ssr] = calc_setpoint


            if ssr_state[ssr] and not ssr_off[ssr]:
                set_ssr(ssr_port, ssr, True)
            else:
                set_ssr(ssr_port, ssr, False)

        time.sleep(pid_cycle_time)

