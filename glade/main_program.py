#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import re

from powershell_engine import Powershell
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

horizontal_scroll = 0
vertical_scroll = 0

def h_scrollbar_event(widget, data, extra = None): 
	print "H SCROLLING", widget
	global horizontal_scroll, vertical_scroll
	if widget.__class__.__name__ == 'Scrollbar':
		value = widget.get_adjustment().get_value()
		horizontal_scroll = int(value)
	elif widget.__class__.__name__ == 'Layout':
		h_value = widget.get_hadjustment().get_value()
		v_value = widget.get_vadjustment().get_value()
	print "horizontal_scroll", horizontal_scroll,  "vertical_scroll", vertical_scroll

def v_scrollbar_event(widget, data, extra = None): 
	print "V SCROLLING", widget
	global horizontal_scroll, vertical_scroll
	if widget.__class__.__name__ == 'Scrollbar':
		value = widget.get_adjustment().get_value()
		vertical_scroll = int(value)
	elif widget.__class__.__name__ == 'Layout':
		h_value = widget.get_hadjustment().get_value()
		v_value = widget.get_vadjustment().get_value()
	print "horizontal_scroll", horizontal_scroll,  "vertical_scroll", vertical_scroll


def scroll_event(widget, data, extra = None): 
	print "SCROLLING ", widget
	global horizontal_scroll, vertical_scroll
	if widget.__class__.__name__ == 'Scrollbar':
		value = widget.get_adjustment().get_value()
		horizontal_scroll = int(value)
	elif widget.__class__.__name__ == 'Layout':
		h_value = widget.get_hadjustment().get_value()
		v_value = widget.get_vadjustment().get_value()
		horizontal_scroll = h_value
		vertical_scroll = v_value
	print "horizontal_scroll", horizontal_scroll,  "vertical_scroll", vertical_scroll


dragging = [False, None]

def clicked_widget( widget, data ):
	global dragging
	print "WIDGET IS CLICKED, ", widget
	dragging = [True, widget]

def released_widget( widget, data ):
	global dragging
	print "WIDGET IS RELEASED, ", widget
	dragging = [False, None]


builder.connect_signals(handlers)

window = builder.get_object('main_window')
fixed_middle = builder.get_object('fixed_middle')
windows_icons = builder.get_object('windows_icons')
linux_icons = builder.get_object('linux_icons')
middle_scroll = builder.get_object('middle_scroll')


# middle_scroll.connect('scroll-child', scroll_event)
fixed_middle.connect('scroll-event', scroll_event)
middle_scroll.get_hscrollbar().connect('change-value', h_scrollbar_event)
middle_scroll.get_vscrollbar().connect('change-value', v_scrollbar_event)

mapping = {
	"windows 10": [ "icons/windows_10_150x150.png", windows_icons],
	"centos": [ "icons/centos_150x150.png", linux_icons],
	"windows xp": [ "icons/windows_xp_150x150.png", windows_icons ],
	"ubuntu": [ "icons/ubuntu_150x150.png", linux_icons ],
	"kali": [ "icons/kali_150x150.png", linux_icons ] ,
	"windows 7": [ "icons/windows_7_150x150.png", windows_icons ],
	"2016": [ "icons/windows_server_2016_150x150.png", windows_icons ],
}



def get_icon_filename( string ):
	global mapping

	for key in mapping:
		if key in string.lower():
			return mapping[key][0]
	return "icons/anything_150x150.png"

def dragging_widget( widget, drag_context, x,y, time ):
	global dragging
	global horizontal_scroll, vertical_scroll

	print "DRAGGING WIDGET", widget, drag_context, time
	print "x", x, ", y", y
	if dragging[0]:
		widget.move(dragging[1], x-75+horizontal_scroll, y-75+vertical_scroll)


def received_drop( widget, drag_context, x,y, data,info, time ):
	global horizontal_scroll, vertical_scroll

	print "RECEIVED DROP!"
	print data.get_text()
	print "x", x, ", y", y

	new_widget = Gtk.EventBox()
	new_widget.set_name('widget')
	new_widget.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [],
            DRAG_ACTION)
	new_widget.drag_source_set_target_list(None)
	new_widget.drag_source_add_text_targets()
	fixed_middle.connect('drag-motion', dragging_widget)
	new_widget.add(Gtk.Image.new_from_file(data.get_text()))
	new_widget.connect('button-press-event', clicked_widget)
	new_widget.connect('button-release-event', released_widget)
	fixed_middle.put( new_widget, x-75 +horizontal_scroll, y-75 +vertical_scroll)
	fixed_middle.show_all()

def begin_drag( widget, data ):
	print "BEGINNING TO DRAG!"

def end_drag( widget, data ):
	global dragging
	print "ENDED DRAG!"
	dragging = [False, None]

def start_drag( widget, drag_context, data, info, time ):
	print "STARTING TO DRAG!"

	selected_path = widget.get_selected_items()[0]
	selected_iter = widget.get_model().get_iter(selected_path)

	# View the selected item, get the text, and map that to the proper image
	filename = get_icon_filename( \
		widget.get_model().get_value(selected_iter, 1) )

	data.set_text(filename, -1)

fixed_middle.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
fixed_middle.connect("drag-data-received", received_drop )
fixed_middle.connect("drag-end", end_drag )

windows_icons.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [],
            DRAG_ACTION)

linux_icons.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [],
            DRAG_ACTION)

fixed_middle.drag_dest_set_target_list(None)
fixed_middle.drag_dest_add_text_targets()

windows_icons.drag_source_set_target_list(None)
windows_icons.drag_source_add_text_targets()
linux_icons.drag_source_set_target_list(None)
linux_icons.drag_source_add_text_targets()

for row in windows_icons.get_model():
	print row[:]

windows_icons.connect('drag-data-get', start_drag)
windows_icons.connect('drag-begin', begin_drag)
linux_icons.connect('drag-data-get', start_drag)
linux_icons.connect('drag-begin', begin_drag)

style_provider = Gtk.CssProvider()
style_provider.load_from_path('sandbox.css')

Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

print "Starting PowerShell..."
powershell = Powershell()
print "Importing PowerCLI..."
powershell.import_powercli()
print "Connecting to server..."
powershell.connect_testing_server()
print "Getting vApps..."

# Grab the vApps..
vapps = powershell.run_command(\
'(Get-ChildItem vmstore:/sandbox_datacenter/datastore1/vapps).Name')

# Cut out the Parentheses...
vapps_list = [ re.sub(r'\s*\(.*\)\s*','',vapp) for vapp in vapps.split('\n') ] 

for vapp in vapps_list:
	added = False
	for key in mapping:
		if key in vapp.lower():
			mapping[key][1].get_model().append(
				[GdkPixbuf.Pixbuf.new_from_file( mapping[key][0] ), vapp ])
			added = True
			break
	if not added:
		windows_icons.get_model().append(
			[GdkPixbuf.Pixbuf.new_from_file( "icons/anything_150x150.png" ), 
			vapp ])

window.show_all()
window.connect('destroy', Gtk.main_quit)
Gtk.main()