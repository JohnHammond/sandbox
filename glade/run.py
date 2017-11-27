#!/usr/bin/env python

import gi
from gi.repository import Gtk
import re

builder = Gtk.Builder()
builder.add_from_file( 'test.glade' )



def ip_entry_activate_cb( widget):

	global builder
	
	content = widget.get_text().strip()
	
	if ( not re.match( r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', content ) ):
		error = builder.get_object('error')
		error.set_text('Please use an IPv4 address.')
	else:
		print "Success!"
	


handlers = {
	"ip_entry_activate_cb": ip_entry_activate_cb,
}




builder.connect_signals(handlers)

window = builder.get_object('vmware_ip_window')
window.show_all()

window.connect('destroy', Gtk.main_quit)
Gtk.main()

