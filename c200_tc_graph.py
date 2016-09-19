import serial, time, io, datetime
from serial.tools.list_ports import comports

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.dates as mdates


data_groups = [[0,1,2,3],[4,5,6],[8,9,10,11],[7,12,13,14,15]]



#outfile_name = "tcdata_" + datetime.datetime.now().strftime("%Y%m%d%H%M.dat")
#print "Writing to ", outfile_name

#outfile = open(outfile_name, "w")


def read_cycle(frame_no,n_tc, time_data, plot_data, tc_data, tc_line, ax_arr):
    time_data.append(datetime.datetime.now())
    for idx in range(n_tc):
        plot_data[idx].append(tc_data[idx])

    for idx,this_curve in enumerate(tc_line):
        if this_curve != None:
            this_curve.set_xdata(time_data)
            this_curve.set_ydata(plot_data[idx])


    for i in range(2):
        for j in range(2):
            ax_arr[i,j].relim()
            ax_arr[i,j].autoscale_view(scalex=False,scaley=True)
#    ax.set_autoscalex_on(True)
#    ax.set_autoscaley_on(True)

            if( datetime.datetime.now() - time_data[0] < datetime.timedelta(minutes=30) ):
                ax_arr[i,j].set_xlim(time_data[0], datetime.datetime.now())
            else:
                ax_arr[i,j].set_xlim(datetime.datetime.now()-datetime.timedelta(minutes=30), datetime.datetime.now())
#ax.set_ylim(20,30)

    return tuple(tc_line)


def plot_loop(n_tc, tc_data):

    plot_data = [[] for i in range(n_tc)]
    time_data = []

    tc_curves = [None for i in range(n_tc)]

    fig, ax_arr = plt.subplots(2,2, figsize=(15,8))

    fig.autofmt_xdate()

    for i in range(2):
        for j in range(2):
            for tc_chan in data_groups[j+2*i]:
                acurve, = ax_arr[i,j].plot([datetime.datetime.now()],[0], label="TC"+str(tc_chan))
                tc_curves[tc_chan] = acurve
            ax_arr[i,j].legend(loc='upper left')
            ax_arr[i,j].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))


    tc_plots = ani.FuncAnimation(fig, read_cycle, fargs=(n_tc, time_data, plot_data, tc_data, tc_curves, ax_arr), blit=True)

    plt.gcf().autofmt_xdate()
    print "Grpah showing"
    plt.show()
