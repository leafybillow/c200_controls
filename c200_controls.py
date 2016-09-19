#!/usr/bin/python

import serial, time, io, datetime, math, gtk

from serial.tools.list_ports import comports

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.dates as mdates

from multiprocessing import Process, Pipe, Array

import c200_ssr, c200_pid, c200_tc, c200_tc_graph, c200_gtk
import c200_write


n_ssr = 2
n_tc = 16


ssr_setp  = Array('f', [0.0  for i in range(n_ssr)] )
ssr_rb    = Array('f', [0.0  for i in range(n_ssr) ] )

pidctrl_state = Array('b', [False for i in range(n_ssr)])
ssr_T_setp   = Array('f', [20.0 for i in range(n_ssr)] )

ssr_T_ramp_state   = Array('b', [False for i in range(n_ssr)] )
ssr_T_ramp   = Array('f', [0.0 for i in range(n_ssr)] )

ssr_tc_setp  = Array('i', [-1 for i in range(n_ssr)] )

ssr_state = Array('b', [False for i in range(n_ssr)])

ssr_avg_power = Array('f', [0.0 for i in range(n_ssr)])

tc_data = Array('f', [0.0 for i in range(n_tc)])
tc_rate = Array('f', [0.0 for i in range(n_tc)])

p_ssr = Process(target = c200_ssr.ssr_loop, args=(n_ssr, ssr_setp,ssr_rb,ssr_state,pidctrl_state))

p_pid = Process(target = c200_pid.pid_loop, args=(ssr_T_setp, ssr_tc_setp, ssr_T_ramp_state, ssr_T_ramp, tc_data, tc_rate, ssr_state, pidctrl_state, ssr_avg_power))

p_tc  = Process(target = c200_tc.tc_loop, args=(n_tc, tc_data, tc_rate))
p_tc_graph  = Process(target = c200_tc_graph.plot_loop, args=(n_tc, tc_data))

p_write = Process(target = c200_write.write, args=(n_tc, n_ssr, ssr_avg_power, tc_data))

# Start alternate processes for controls
p_ssr.start()
p_pid.start()
p_tc.start()
p_tc_graph.start()
p_write.start()

ssr_setp[0] = 50.0


controls = c200_gtk.c200_controls()

controls.n_tc  = n_tc
controls.n_ssr = n_ssr

controls.tc_process       =  p_tc
controls.tc_graph_process =  p_tc_graph
controls.ssr_process      = p_ssr
controls.pid_process      = p_pid

controls.ssr_setp = ssr_setp
controls.ssr_rb   = ssr_rb

controls.pidctrl_state = pidctrl_state
controls.ssr_T_setp = ssr_T_setp
controls.ssr_T_ramp_state = ssr_T_ramp_state
controls.ssr_T_ramp = ssr_T_ramp
controls.ssr_tc_setp = ssr_tc_setp
controls.ssr_state = ssr_state
controls.ssr_avg_power = ssr_avg_power
controls.tc_data = tc_data
controls.tc_rate = tc_rate

controls.main()



