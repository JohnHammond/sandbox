#!/usr/bin/env python

import gi
from gi.repository import Gtk
import re

builder = Gtk.Builder()
builder.add_from_file( 'list.glade' )


def ip_entry_activate_cb( widget):

	global builder
	
	content = widget.get_text().strip()
	
	if ( not re.match( r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', content ) ):
		error = builder.get_object('error')
		error.set_text('Please use an IPv4 address.')
	else:
		print "Success!"
	

def on_enabled_toggle_toggled( widget, path ):
	global provisioning_features

	provisioning_features[path][1] = not provisioning_features[path][1]


def ok_button_activate_cb( widget ):
	global provisioning_features

	item = provisioning_features.get_iter_first ()

	while ( item != None ):
		print provisioning_features[item][0]

		item = provisioning_features.iter_next(item)


def close_window(widget):
	Gtk.main_quit()

handlers = {
	"ip_entry_activate_cb": ip_entry_activate_cb,
	"on_enabled_toggle_toggled": on_enabled_toggle_toggled,
	"ok_button_activate_cb": ok_button_activate_cb,
	"close_window": close_window,
}

builder.connect_signals(handlers)

window = builder.get_object('window')
provisioning_features = builder.get_object('provisioning_features')
provisioning_treeview = builder.get_object('provisioning_treeview')
window.show_all()

window.connect('destroy', Gtk.main_quit)
Gtk.main()