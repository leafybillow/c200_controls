import serial, time, io, datetime
from serial.tools.list_ports import comports

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.dates as mdates


data_groups = [[1,2,3,5,4],[15,6,7],[9,13,16,14],[10,12,11]]



#outfile_name = "tcdata_" + datetime.datetime.now().strftime("%Y%m%d%H%M.dat")
#print "Writing to ", outfile_name

#outfile = open(outfile_name, "w")

ax_arr = None
fig = None

def flatten( arr ):
    compl = []
    for i in arr:
        compl += i
    return compl


def read_cycle(frame_no,n_tc,n_ssr, time_data, plot_data, ssr_plot_data, tc_data, ssr_data, ssr_power_data, tc_line, ssr_line, dummy):
    global ax_arr
    time_data.append(datetime.datetime.now())
    flatchan = flatten(data_groups)

    for idx in range(len(flatten(data_groups))):
        plot_data[idx].append( tc_data[flatchan[idx]-1] ) 
        tc_line[idx].set_xdata(time_data)
        tc_line[idx].set_ydata(plot_data[idx])

    for idx in range(n_ssr):
        if ssr_data[idx]:
            ssr_plot_data[n_ssr+idx].append( 1.0) 
        else:
            ssr_plot_data[n_ssr+idx].append( 0.0) 
        ssr_line[idx+n_ssr].set_xdata(time_data)
        ssr_line[idx+n_ssr].set_ydata(ssr_plot_data[n_ssr+idx])

    for idx in range(n_ssr):
        ssr_plot_data[idx].append( ssr_power_data[idx] ) 
        ssr_line[idx].set_xdata(time_data)
        ssr_line[idx].set_ydata(ssr_plot_data[idx])

    for i in range(3):
        for j in range(2):

            ax_arr[i,j].relim()
            ax_arr[i,j].autoscale_view(scalex=False,scaley=True)

            if( datetime.datetime.now() - time_data[0] < datetime.timedelta(minutes=30) ):
                ax_arr[i,j].set_xlim(time_data[0], datetime.datetime.now())
            else:
                ax_arr[i,j].set_xlim(datetime.datetime.now()-datetime.timedelta(minutes=30), datetime.datetime.now())


    ax_arr[2,0].set_ylim(-0.05, 1.05)
    ax_arr[2,1].set_ylim(-0.05, 1.05)

    return tuple(tc_line+ssr_line),


def plot_loop(n_tc, tc_data, n_ssr, ssr_data, ssr_power_data):

    global ax_arr
    global fig

    plot_data = [[] for i in range(len(flatten(data_groups)))]
    ssr_plot_data = [[] for i in range(2*n_ssr)]
    time_data = []


    temp_fig, temp_ax_arr = plt.subplots(3,2, figsize=(15,8))
    fig = temp_fig
    ax_arr = temp_ax_arr

    tc_curves = []
    ssr_curves = []

    fig.autofmt_xdate()

    for i in range(2):
        for j in range(2):
            for tc_chan in data_groups[j+2*i]:
                acurve, = ax_arr[i,j].plot([datetime.datetime.now()],[25], label="TC %2d"%tc_chan )
                tc_curves.append(acurve)
            ax_arr[i,j].legend(loc='upper left')
            ax_arr[i,j].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax_arr[i,j].set_ylabel("Temp [degC]")

    for i in range(n_ssr):
        acurve, = ax_arr[2,0].plot([datetime.datetime.now()],[0.0], label="SSR %d "% i)
        ssr_curves.append(acurve)
    ax_arr[2,0].legend(loc='upper left')
    ax_arr[2,0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax_arr[2,0].set_ylabel("Average Power")

    for i in range(n_ssr):
        acurve, = ax_arr[2,1].plot([datetime.datetime.now()],[0.0], label="SSR %d "% i)
        ssr_curves.append(acurve)
    ax_arr[2,1].legend(loc='upper left')
    ax_arr[2,1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax_arr[2,1].set_ylabel("SSR State")


    tc_plots = ani.FuncAnimation(fig, read_cycle, interval=2000, fargs=(n_tc, n_ssr, time_data, plot_data, ssr_plot_data, tc_data, ssr_data, ssr_power_data, tc_curves, ssr_curves, ax_arr), blit=False)

    plt.gcf().autofmt_xdate()
    plt.show()
