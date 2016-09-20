import serial, time, io, datetime
from serial.tools.list_ports import comports

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.dates as mdates


data_groups = [[1,2,3,4],[5,6,7,9],[11,12,13,16],[10,14,15]]



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


def read_cycle(frame_no,n_tc, time_data, plot_data, tc_data, tc_line, dummy):
    global ax_arr
    time_data.append(datetime.datetime.now())
    flatchan = flatten(data_groups)

    for idx in range(len(flatten(data_groups))):
        plot_data[idx].append( tc_data[flatchan[idx]-1] ) 
        tc_line[idx].set_xdata(time_data)
        tc_line[idx].set_ydata(plot_data[idx])

    for i in range(2):
        for j in range(2):

            ax_arr[i,j].relim()
            ax_arr[i,j].autoscale_view(scalex=False,scaley=True)

            if( datetime.datetime.now() - time_data[0] < datetime.timedelta(minutes=30) ):
                ax_arr[i,j].set_xlim(time_data[0], datetime.datetime.now())
            else:
                ax_arr[i,j].set_xlim(datetime.datetime.now()-datetime.timedelta(minutes=30), datetime.datetime.now())

#    plt.flush() 
    return tuple(tc_line),


def plot_loop(n_tc, tc_data):

    global ax_arr
    global fig

    plot_data = [[] for i in range(len(flatten(data_groups)))]
    time_data = []


    temp_fig, temp_ax_arr = plt.subplots(2,2, figsize=(15,8))
    fig = temp_fig
    ax_arr = temp_ax_arr

    tc_curves = []

    fig.autofmt_xdate()

    for i in range(2):
        for j in range(2):
            for tc_chan in data_groups[j+2*i]:
                acurve, = ax_arr[i,j].plot([datetime.datetime.now()],[25], label="TC %2d"%tc_chan )
                tc_curves.append(acurve)
            ax_arr[i,j].legend(loc='upper left')
            ax_arr[i,j].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))


    tc_plots = ani.FuncAnimation(fig, read_cycle, interval=2000, fargs=(n_tc, time_data, plot_data, tc_data, tc_curves, ax_arr), blit=False)

    plt.gcf().autofmt_xdate()
    plt.show()
