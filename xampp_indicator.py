#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# XAMPP Indicator
#
# Authors: Álvaro Larumbe <biobiotm@gmail.com>
#

import os
import subprocess
import time
from gi.repository import Gtk
from gi.repository import AppIndicator3 as Appindicator

xampp_path = "/opt/lampp"
xampp_bin = os.path.join(xampp_path, "lampp")
menu_ws = None
menu_db = None
menu_ftp = None
menu_ws_signal = None
menu_db_signal = None
menu_ftp_signal = None
WS = "apache"
DB = "mysql"
FTP = "ftp"
RUN = "RUNNING"
STOP = "NOTRUNNING"
DEAC = "DEACTIVATED"


# Returns a string representing a call to the xampp script
def get_xampp_command(command):
    xampp_command = "%s %s" % (xampp_bin, command)
    return xampp_command


# Returns a dictionary of service statues by calling "lammp statusraw" like this
def get_statuses():
    # Get status of the services
    raw_status = subprocess.getoutput(get_xampp_command("statusraw"))
    lines = raw_status.split("\n")

    # Delete an extra line appearing if MySQL is running due to permissions
    if len(lines) > 4:
        lines.pop(2)

    # Ignore first line, and create a dictionary of service/status
    # pairs by splitting each line around the central whitespace
    statuses = dict([line.split(" ") for line in lines[1:]])
    # for key, value in sorted(statuses.items()):
    #     print("{}: {}".format(key, value))
    # print()
    return statuses


# Execute the XAMPP binary with "command" as arguments
def execute_xampp_command(command):
    p = subprocess.call([xampp_bin, command])
    return p


# Execute the XAMPP binary with "command" as arguments with gksudo
def execute_xampp_command_gksudo(command):
    p = subprocess.call(["gksudo", xampp_bin, command])
    return p


# Start service passed by args
def start_xampp_service(gtkmenuitem, service):
    execute_xampp_command_gksudo("start" + service)
    time.sleep(2)
    update_status()


# Stop service passed by args
def stop_xampp_service(gtkmenuitem, service):
    execute_xampp_command_gksudo("stop" + service)
    time.sleep(2)
    update_status()


# Create menu items for each XAMPP service and a exit entry
def create_menu_items():
    global menu_ws
    global menu_db
    global menu_ftp

    menu_ws = Gtk.MenuItem("Apache")
    menu.append(menu_ws)
    menu_ws.show()

    menu_db = Gtk.MenuItem("MySQL")
    menu.append(menu_db)
    menu_db.show()

    menu_ftp = Gtk.MenuItem("ProFTPD")
    menu.append(menu_ftp)
    menu_ftp.show()

    update_status()

    menu_item = Gtk.SeparatorMenuItem()
    menu.append(menu_item)
    menu_item.show()

    menu_exit = Gtk.MenuItem("Exit")
    menu.append(menu_exit)
    menu_exit.connect("activate", Gtk.main_quit)
    menu_exit.show()


# Update menu items status
def update_status():
    global menu_ws
    global menu_db
    global menu_ftp
    global menu_ws_signal
    global menu_db_signal
    global menu_ftp_signal

    all_statuses = get_statuses()

    # Update labels
    menu_ws.set_label("Apache\t-\t%s" % all_statuses["APACHE"])
    menu_db.set_label("MySQL\t-\t%s" % all_statuses["MYSQL"])
    menu_ftp.set_label("ProFTPD\t-\t%s" % all_statuses["PROFTPD"])

    # Connect signals for Apache
    if all_statuses["APACHE"] == STOP:
        try:
            menu_ws.disconnect(menu_ws_signal)
        except TypeError:
            None
        menu_ws_signal = menu_ws.connect("activate", start_xampp_service, WS)
    else:
        try:
            menu_ws.disconnect(menu_ws_signal)
        except TypeError:
            None
        menu_ws_signal = menu_ws.connect("activate", stop_xampp_service, WS)

    # Connect signals for MySQL
    if all_statuses["MYSQL"] == STOP:
        try:
            menu_db.disconnect(menu_db_signal)
        except TypeError:
            None
        menu_db_signal = menu_db.connect("activate", start_xampp_service, DB)
    else:
        try:
            menu_db.disconnect(menu_db_signal)
        except TypeError:
            None
        menu_db_signal = menu_db.connect("activate", stop_xampp_service, DB)

    # Connect signals for ProFTPD
    if (all_statuses["PROFTPD"] == STOP) | (all_statuses["PROFTPD"] == DEAC):
        try:
            menu_ftp.disconnect(menu_ftp_signal)
        except TypeError:
            None
        menu_ftp_signal = menu_ftp.connect("activate", start_xampp_service, FTP)
    else:
        try:
            menu_ftp.disconnect(menu_ftp_signal)
        except TypeError:
            None
        menu_ftp_signal = menu_ftp.connect("activate", stop_xampp_service, FTP)


if __name__ == "__main__":
    ind = Appindicator.Indicator.new("xampp-indicator",
                                     "xampp",
                                     Appindicator.IndicatorCategory.APPLICATION_STATUS)
    ind.set_status(Appindicator.IndicatorStatus.ACTIVE)

    menu = Gtk.Menu()
    create_menu_items()
    ind.set_menu(menu)
    Gtk.main()
