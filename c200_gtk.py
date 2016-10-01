
import pygtk
pygtk.require('2.0')
import gtk, gobject,glib,time

class c200_controls:
    n_tc  = 0
    n_ssr = 0

    ssr_setp = None
    ssr_rb   = None
    pidctrl_state = None
    ssr_T_setp = None
    ssr_T_ramp_state = None
    ssr_T_ramp = None
    ssr_T_prop = None
    ssr_tc_setp = None
    ssr_state = None
    ssr_avg_power = None
    tc_data = None
    tc_rate = None
    ssr_off = None

    pid_process = None
    ssr_process = None
    tc_process  = None
    tc_graph_process = None

    tc_data_labels = []
    tc_rate_min_labels = []
    tc_rate_hour_labels = []

    ssr_power_labels = []
    ssr_max_power_box = []
    ssr_state_labels = []

    ssr_setpoint_box = []
    ssr_readback_labels = []

    ssr_tc_setpoint_box = []
    ssr_prop_setpoint_box = []
    ssr_rate_setpoint_box = []

    ssr_tc_assigned_label= []
    ssr_tc_readback_label= []
    ssr_prop_readback_label= []
    ssr_rate_readback_label= []


    ssr_tc_select_menu = []

    ssr_tc_rate_check = []

    ssr_man_pid_radio  = []

    off_buttons = []

    def hello(self, widget, data=None):
        print "Hello"

    def update_vals(self):
        for idx, tc in enumerate(self.tc_data_labels):
            tc.set_text( "%3.1f" % self.tc_data[idx] )

        for idx, tc in enumerate(self.tc_rate_min_labels):
            tc.set_text( "%+3.1f"% (self.tc_rate_min[idx]*60.0) )

        for idx, tc in enumerate(self.tc_rate_hour_labels):
            tc.set_text( "%+3.1f"% (self.tc_rate_hour[idx]*3600.0) )

        for idx, ssr in enumerate(self.ssr_power_labels):
            max_p_val = 400.0
            try:
                max_p_val = float(self.ssr_max_power_box[idx].get_text())
            except:
                max_p_val = 100.0

            ssr.set_text( "%4.1f / %4.1f W"% ( (self.ssr_avg_power[idx]*max_p_val) , max_p_val ) )

        for idx, ssr in enumerate(self.ssr_state_labels):
            if self.ssr_state[idx]:
                ssr.set_text( "ON ")
            else:
                ssr.set_text( "OFF")

        for idx, ssr in enumerate(self.ssr_readback_labels):
            ssr.set_text( "%2.0f%%"% self.ssr_rb[idx]) 

        for idx, off_button in enumerate(self.off_buttons):
            if self.ssr_off[idx]:
                off_button.set_active(False)
                off_button.set_label("OFF")
            else:
                off_button.set_active(True)
                off_button.set_label("ON")

        # PID controls readback
        for idx, ssr in enumerate(self.ssr_tc_assigned_label):
            ssr.set_text( "TC %2d" % (self.ssr_tc_setp[idx]+1)) 

        for idx, ssr in enumerate(self.ssr_tc_readback_label):
            ssr.set_text( "%4.1f" % self.ssr_T_setp[idx]) 

        for idx, ssr in enumerate(self.ssr_prop_readback_label):
            ssr.set_text( "%4.1f" % (self.ssr_T_prop[idx]*100.0)) 

        for idx, ssr in enumerate(self.ssr_rate_readback_label):
            ssr.set_text( "%4.1f" % (self.ssr_T_ramp[idx]*60.0)) 

        return True
        
    def set_ssr_max(self, entry, ssr):
        self.update_vals()

    def set_ssr_man(self, entry, ssr):
        setpoint = 0.0
        try:
            setpoint = float(entry.get_text())
        except:
            setpoint = 0.0

        print "Seting to ", setpoint
        self.ssr_setp[ssr] = setpoint
        self.update_vals()

    def man_pid_select(self, widget, ssr, val):
        self.pidctrl_state[ssr] = val

    def set_pid_tc(self, cbox, ssr):
        self.ssr_tc_setp[ssr] = cbox.get_active()

    def set_pid_setpoint(self, data, ssr):
        setpoint = 20.0
        try:
            setpoint = float(data.get_text())
        except:
            setpoint = 20.0
        self.ssr_T_setp[ssr] = setpoint

    def set_rate_setpoint(self, data, ssr):
        setpoint = -100.0
        try:
            setpoint = float(data.get_text())
        except:
            setpoint = -100.0
        self.ssr_T_ramp[ssr] = setpoint/60.0

    def set_prop_setpoint(self, data, ssr):
        setpoint = 0.0
        try:
            setpoint = float(data.get_text())
        except:
            setpoint = -0.0
        self.ssr_T_prop[ssr] = setpoint/100.0


    def set_rate_limit(self, wid, ssr):
        if wid.get_active():
            self.ssr_T_ramp_state[ssr] = True
        else:
            self.ssr_T_ramp_state[ssr] = False


    def turn_off_ssr(self, wid, ssr):
        if wid.get_active():
            self.ssr_off[ssr] = False
            wid.set_label("ON")
            print "Manually turning on ssr ", ssr
        else:
            self.ssr_off[ssr] = True
            wid.set_label("OFF")
            print "Manually turning off ssr ", ssr


    def delete_event(self, widget, event, data=None):
        print "Killing everything"
        self.pid_process.terminate()
        self.ssr_process.terminate()
        self.tc_process.terminate()
        self.tc_graph_process.terminate()
        return False

    def destroy(self, widget, data=None):
        print "Killing everything"
        self.pid_process.terminate()
        self.ssr_process.terminate()
        self.tc_process.terminate()
        self.tc_graph_process.terminate()

        gtk.main_quit()

    def __init__(self):
        gobject.timeout_add(100, self.update_vals)
        return

    def main(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)

        self.window.set_border_width(10)

        main_box  = gtk.HBox(homogeneous=False, spacing=2)


        tc_box  = gtk.VBox(homogeneous=False, spacing=0)
        tc_head_box = gtk.HBox(homogeneous=False, spacing=2)
        label= gtk.Label("Chan")
        tc_head_box.pack_start(label, expand=True, fill=True, padding=0)
        label.show()

        label= gtk.Label("Temp\n[degC]")
        tc_head_box.pack_start(label, expand=True, fill=True, padding=0)
        label.show()

        label= gtk.Label("Rate\n[K/min]")
        tc_head_box.pack_start(label, expand=True, fill=True, padding=0)
        label.show()
        label= gtk.Label("Rate\n[K/hr]")
        tc_head_box.pack_start(label, expand=True, fill=True, padding=0)
        label.show()

        tc_box.pack_start(tc_head_box, expand=True, fill=True, padding=0)
        tc_head_box.show()

        self.tc_data_labels = []
        self.tc_rate_min_labels = []
        self.tc_rate_hour_labels = []
        for i in range(self.n_tc):
            tc_chan_box = gtk.HBox(homogeneous=False, spacing=2)

            label= gtk.Label("TC %2d" % (i+1))
            tc_chan_box.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            label= gtk.Label("temp")
            tc_chan_box.pack_start(label, expand=True, fill=True, padding=0)
            label.show()
            self.tc_data_labels.append(label)

            label= gtk.Label("rate [degC/min]")
            tc_chan_box.pack_start(label, expand=True, fill=True, padding=0)
            label.show()
            self.tc_rate_min_labels.append(label)

            label= gtk.Label("rate [degC/hour]")
            tc_chan_box.pack_start(label, expand=True, fill=True, padding=0)
            label.show()
            self.tc_rate_hour_labels.append(label)

            tc_box.pack_start(tc_chan_box, expand=True, fill=True, padding=0)
            tc_chan_box.show()

        main_box.pack_start(tc_box, expand=True, fill=True, padding=0)
        tc_box.show()
            
        ssr_box  = gtk.VBox(homogeneous=False, spacing=0)

        for i in range(self.n_ssr):
            ssr_single_ssr_box = gtk.HBox(homogeneous=False, spacing=0)

            ssr_chanbox = gtk.VBox(homogeneous=False, spacing=0)

            label = gtk.Label("SSR %d" % i)
            ssr_chanbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            # Need avg power, max power , State, input
            ssr_powerbox = gtk.HBox(homogeneous=False, spacing=0)
            label = gtk.Label("0/0 W")
            ssr_powerbox.pack_start(label, expand=True, fill=True, padding=0)
            self.ssr_power_labels.append(label)
            label.show()

            label = gtk.Label("???")
            ssr_powerbox.pack_start(label, expand=True, fill=True, padding=0)
            self.ssr_state_labels.append(label)
            label.show()

            entry = gtk.Entry(max=0)
            ssr_powerbox.pack_start(entry, expand=True, fill=True, padding=0)
            self.ssr_max_power_box.append(entry)
            entry.connect("activate", self.set_ssr_max, i)
            entry.show()

            label = gtk.Label("W Max")
            ssr_powerbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            ssr_chanbox.pack_start(ssr_powerbox, expand=True, fill=True, padding=0)
            ssr_powerbox.show()


            #############################################
            ssr_ctrlbox = gtk.HBox(homogeneous=False, spacing=0)

            ssr_radiobox = gtk.VBox(homogeneous=False, spacing=0)

            man_rad = gtk.RadioButton(group=None, label="Manual")
            man_rad.connect("toggled", self.man_pid_select, i, False)
            ssr_radiobox.pack_start(man_rad, expand=True, fill=True, padding=0)
            man_rad.show()

            pid_rad = gtk.RadioButton(group=man_rad, label="PID")
            pid_rad.connect("toggled", self.man_pid_select, i, True)
            ssr_radiobox.pack_start(pid_rad, expand=True, fill=True, padding=0)
            pid_rad.show()

            if self.pidctrl_state[i]:
                pid_rad.set_active(True)
            else:
                man_rad.set_active(True)

            ssr_ctrlbox.pack_start(ssr_radiobox, expand=True, fill=True, padding=0)
            ssr_radiobox.show()


            ############## First line - manual setpoint
            ssr_input_ctrlbox = gtk.VBox(homogeneous=False, spacing=0)

            ssr_man_ctrlbox = gtk.HBox(homogeneous=False, spacing=0)

            label = gtk.Label("   %")
            ssr_man_ctrlbox.pack_start(label, expand=True, fill=True, padding=0)
            self.ssr_readback_labels.append(label)
            label.show()

            entry = gtk.Entry(max=0)
            ssr_man_ctrlbox.pack_start(entry, expand=True, fill=True, padding=0)
            self.ssr_setpoint_box.append(entry)
            entry.connect("activate", self.set_ssr_man, i)
            entry.show()

            label = gtk.Label("%")
            ssr_man_ctrlbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            ssr_input_ctrlbox.pack_start(ssr_man_ctrlbox, expand=True, fill=True, padding=0)
            ssr_man_ctrlbox.show()

            ############## Second line - PID setpoint
            ssr_pid_ctrlbox = gtk.HBox(homogeneous=False, spacing=0)

            combobox = gtk.combo_box_new_text()
            for tc  in range(self.n_tc):
                combobox.append_text("TC %2d" % (tc+1))
            self.ssr_tc_select_menu.append(combobox)
            combobox.connect("changed", self.set_pid_tc, i)
            ssr_pid_ctrlbox.pack_start(combobox, expand=True, fill=True, padding=0)
            combobox.show()

            label = gtk.Label("Set Temp:")
            ssr_pid_ctrlbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()


            entry = gtk.Entry(max=0)
            ssr_pid_ctrlbox.pack_start(entry, expand=True, fill=True, padding=0)
            self.ssr_tc_setpoint_box.append(entry)
            entry.connect("activate", self.set_pid_setpoint, i)
            entry.show()

            label = gtk.Label("degC")
            ssr_pid_ctrlbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            label = gtk.Label("prop dT:")
            ssr_pid_ctrlbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            entry = gtk.Entry(max=0)
            ssr_pid_ctrlbox.pack_start(entry, expand=True, fill=True, padding=0)
            self.ssr_tc_setpoint_box.append(entry)
            entry.connect("activate", self.set_prop_setpoint, i)
            entry.show()

            label = gtk.Label("%/degC")
            ssr_pid_ctrlbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()


            check = gtk.CheckButton(label="Rate Limit")
            ssr_pid_ctrlbox.pack_start(check, expand=True, fill=True, padding=0)
            self.ssr_tc_rate_check.append(check)
            check.connect("toggled", self.set_rate_limit, i)
            if self.ssr_T_ramp_state[i]:
                check.set_active(True)
            check.show()

            entry = gtk.Entry(max=0)
            ssr_pid_ctrlbox.pack_start(entry, expand=True, fill=True, padding=0)
            self.ssr_rate_setpoint_box.append(entry)
            entry.connect("activate", self.set_rate_setpoint, i)
            entry.show()


            label = gtk.Label("degC/min")
            ssr_pid_ctrlbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            ssr_input_ctrlbox.pack_start(ssr_pid_ctrlbox, expand=True, fill=True, padding=0)
            ssr_pid_ctrlbox.show()

            ############## Third line - PID readback
            ssr_pid_rbbox = gtk.HBox(homogeneous=False, spacing=0)

            label = gtk.Label("TC -1")
            self.ssr_tc_assigned_label.append(label)
            ssr_pid_rbbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            label = gtk.Label("Set Temp:")
            ssr_pid_rbbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            label = gtk.Label("0.0")
            self.ssr_tc_readback_label.append(label)
            ssr_pid_rbbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            label = gtk.Label("degC")
            ssr_pid_rbbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            label = gtk.Label("prop dT:")
            ssr_pid_rbbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            label = gtk.Label("0.0")
            self.ssr_prop_readback_label.append(label)
            ssr_pid_rbbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()


            label = gtk.Label("%/degC")
            ssr_pid_rbbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()


            # empty space here

            label = gtk.Label("0.0")
            self.ssr_rate_readback_label.append(label)
            ssr_pid_rbbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()


            label = gtk.Label("degC/min")
            ssr_pid_rbbox.pack_start(label, expand=True, fill=True, padding=0)
            label.show()

            ssr_input_ctrlbox.pack_start(ssr_pid_rbbox, expand=True, fill=True, padding=0)
            ssr_pid_rbbox.show()


            ################################



            ssr_ctrlbox.pack_start(ssr_input_ctrlbox,  expand=True, fill=True, padding=0)
            ssr_input_ctrlbox.show()

            ssr_chanbox.pack_start(ssr_ctrlbox, expand=True, fill=True, padding=0)
            ssr_ctrlbox.show()


            ssr_single_ssr_box.pack_start(ssr_chanbox, expand=True, fill=True, padding=0)
            ssr_chanbox.show()

            button = gtk.ToggleButton("ON")
            button.set_active(True)
            button.connect("toggled", self.turn_off_ssr, i)
            self.off_buttons.append(button)

            ssr_single_ssr_box.pack_start( button, expand=True, fill=True, padding=5)
            button.show()

            ssr_box.pack_start(ssr_single_ssr_box, expand=True, fill=True, padding=0)
            ssr_single_ssr_box.show()

        main_box.pack_start(ssr_box, expand=True, fill=True, padding=0)
        ssr_box.show()

        self.window.add(main_box)
        main_box.show()

        self.window.show()
        gtk.main()
