#!/usr/bin/env python

import gi
from gi.repository import Gtk, Gdk
import re

builder = Gtk.Builder()
builder.add_from_file( 'gui.glade' )


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

window = builder.get_object('main_window')
drawing_area = builder.get_object('drawing_area')

white = Gdk.color_parse("AliceBlue")
white = Gdk.RGBA.from_color(white)
drawing_area.override_background_color(0, white)
drawing_area.show_all()
window.show_all()
window.connect('destroy', Gtk.main_quit)
Gtk.main()