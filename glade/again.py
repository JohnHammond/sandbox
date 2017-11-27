#!/usr/bin/env python

import gi
from gi.repository import Gtk, Gdk
import re

builder = Gtk.Builder()
builder.add_from_file( 'gui.glade' )

DRAG_ACTION = Gdk.DragAction.COPY

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


def received_drop( widget, drag_context, x,y, data,info, time ):
	print "RECEIVED DROP!"
	print data.get_text()
	print "x", x, ", y", y

def begin_drag( widget, data ):
	print "BEGINNING TO DRAG!"

def end_drag( widget, data ):
	print "ENDED DRAG!"


def start_drag( widget, drag_context, data, info, time ):
	print "STARTING TO DRAG!"

	selected_path = widget.get_selected_items()[0]
	selected_iter = widget.get_model().get_iter(selected_path)

	data.set_text('Data being passed...', -1)

builder.connect_signals(handlers)

window = builder.get_object('main_window')
fixed_middle = builder.get_object('fixed_middle')
windows_icons = builder.get_object('windows_icons')

fixed_middle.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
fixed_middle.connect("drag-data-received", received_drop )
fixed_middle.connect("drag-end", end_drag )


windows_icons.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [],
            DRAG_ACTION)

fixed_middle.drag_dest_set_target_list(None)
fixed_middle.drag_dest_add_text_targets()
windows_icons.drag_source_set_target_list(None)
windows_icons.drag_source_add_text_targets()

windows_icons.connect('drag-data-get', start_drag)
windows_icons.connect('drag-begin', begin_drag)

style_provider = Gtk.CssProvider()
style_provider.load_from_path('sandbox.css')

Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

window.show_all()
window.connect('destroy', Gtk.main_quit)
Gtk.main()