import serial, time, io, datetime, math
from serial.tools.list_ports import comports

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.dates as mdates

from multiprocessing import Process, Pipe, Array


ssr_cycle_time = 5.0; # time in s for SSR cycle
granularity = 100;

def ssr_loop(n_ssr, ssr_off, setpoint, readback, ssr_state, pidctrl_state):
    tick = ssr_cycle_time/granularity

    # Space out cycles

    start_tick = [ time.time() +  ssr_cycle_time*(i+1)/(float(n_ssr)) for i in range(n_ssr)]

    while 1:
        for idx,p in enumerate(setpoint):
            # PID directly sets readback
            if not pidctrl_state[idx]:
                readback[idx] = p
        now = float(time.time())

        next_ev = ssr_cycle_time/5.0 # don't sleep for longer than this


        for ssr in range(n_ssr):
            if ssr_off[ssr]:
                ssr_state[ssr] = False
            else:
                t_in_cycle = math.fmod(now - start_tick[ssr], ssr_cycle_time)

                if 0.0 <= t_in_cycle/ssr_cycle_time and t_in_cycle/ssr_cycle_time < readback[ssr]/100.0:
                    ssr_state[ssr] = True 
                    # SSR turned on in PID
                else:
                    ssr_state[ssr] = False
                    # SSR turned off in PID

                if t_in_cycle/ssr_cycle_time < 0.0 and abs(t_in_cycle) < next_ev:
                    next_ev = abs(t_in_cycle)

                if ssr_state[ssr]:
                    t_left = ssr_cycle_time*readback[ssr]/100.0 - t_in_cycle
                    if t_left < next_ev and t_left > 0.0:
                        next_ev = t_left
                else:
                    t_left = ssr_cycle_time - t_in_cycle
                    if t_left < next_ev and t_left > 0.0:
                        next_ev = t_left

        time.sleep(next_ev)

