#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import re

from powershell_engine import Powershell
builder = Gtk.Builder()
builder.add_from_file( 'gui.glade' )

DRAG_ACTION = Gdk.DragAction.COPY

def set_vm_name_display(current_text):
	to_set = '<span color="gray" font="30">'+current_text+'</span>'

	if current_text == '':
		to_set = '<span color="gray" font="30">'+' '+'</span>'
	if len(current_text) > 14:
		to_set = '<span color="gray" font="30">'+current_text[:11]+\
		'...</span>'

	vm_name_label.set_markup(to_set)

class VM:
	'''
	This is a `backend` object that just contains data. The `VMIcon` class
	has the functionality for the GTK/GUI frontend.
	'''
	def __init__( self ):

		self.hostname = 'virtual-machine'
		self.ip_method = 'static'
		
		# self.ip_address = ''
		self.hdd = 50 # GB
		self.cpu = 1 # #
		self.ram = 2 # GB

		self.esxi_host = ''


class VMIcon():

	def __init__( self, image_filename):

		# Create the backend virtual machine object...
		self.vm = VM()

		# Define the GUI controls...
		self.selected = False

		self.container = Gtk.EventBox()
		self.container.parent = self
		self.image_widget = Gtk.Image.new_from_file(image_filename)
		self.vbox_widget = Gtk.Box( orientation=Gtk.Orientation.VERTICAL )
		self.entry_widget = Gtk.Entry()
		self.entry_widget.set_alignment(0.5)
		self.entry_widget.connect('changed', self.text_changed)

		# This is specifically for CSS styling...
		self.entry_widget.set_name('vmname_entry')

		self.entry_widget.set_text('New VM')

		self.vbox_widget.pack_start(self.image_widget, True, True, 0)
		self.vbox_widget.pack_start(self.entry_widget, True, True, 0)
		self.container.add(self.vbox_widget)

		self.container.connect('button-press-event', self.mouse_press)
		self.container.connect('button-release-event', self.mouse_release)

		# Allow the user to move it in the display
		self.enable_drag_and_drop()

	def enable_drag_and_drop( self ):
		self.container.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], \
             DRAG_ACTION)
		self.container.drag_source_set_target_list(None)
		self.container.drag_source_add_text_targets()


	def text_changed( self, widget, data = None ):
		print "VMICON TEXT CHANGED!"
		print widget.get_text()
		if self.selected:
			set_vm_name_display( self.entry_widget.get_text() ) 


	def mouse_press( self, widget, data ):
		global dragging
		print "VMICON IS CLICKED, ", widget
		print data
		if data.type == Gdk.EventType._2BUTTON_PRESS:
			print "*** DOUBLE CLICKED! ***"


		deselect_all()
		self.select()
		dragging = [True, self.container]

	def select( self ):
		global dragging, vm_name_label


		self.selected = True
		self.container.set_name('selected')
		set_vm_name_display( self.entry_widget.get_text() ) 

		# Update the left side display..
		hostname_entry.set_text( self.vm.hostname )
		hdd_spin_button.set_value( self.vm.hdd )
		cpu_spin_button.set_value( self.vm.cpu )
		ram_spin_button.set_value( self.vm.ram )

	def unselect():
		global dragging

		self.selected = False
		deselect_all()
		self.container.set_name('nothing')


	def mouse_release( self, widget, data ):
		
		global dragging
		print "VMICON IS RELEASED, ", widget
		deselect_all()
		self.container.set_name('selected')
		
		dragging = [False, None]


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




window = builder.get_object('main_window')
fixed_middle = builder.get_object('fixed_middle')
vm_name_label = builder.get_object('vm_name_label')
hostname_entry = builder.get_object('hostname_entry')

hdd_spin_button = builder.get_object('hdd_spin_button')
cpu_spin_button = builder.get_object('cpu_spin_button')
ram_spin_button = builder.get_object('ram_spin_button')
fixed_middle_event_box = builder.get_object('fixed_middle_event_box')
windows_icons = builder.get_object('windows_icons')
linux_icons = builder.get_object('linux_icons')
middle_scroll = builder.get_object('middle_scroll')

def hostname_entry_changed( widget, data = None ):
	print "HOSTNAME ENTRY CLICKED"
	virtual_machines = fixed_middle.get_children()
	for vm in virtual_machines:
		if ( vm.get_name() == 'selected' ):
			print vm.parent

hostname_entry.connect('changed', hostname_entry_changed)

def deselect_all():
	for each in fixed_middle.get_children(): each.set_name('nothing')


def middle_pressed( widget, data ):
	print "Middle Section pressed!"
	# deselect_all()

def middle_released( widget, data ):
	print "Middle Section released!"
	# deselect_all()


fixed_middle.connect('scroll-event', scroll_event)
fixed_middle_event_box.connect('button-press-event', middle_pressed)
fixed_middle_event_box.connect('button-release-event', middle_released)
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

	vmicon = VMIcon( data.get_text() )
	fixed_middle.connect('drag-motion', dragging_widget)

	fixed_middle.put( vmicon.container, x-75 +horizontal_scroll, y-75 +vertical_scroll)
	fixed_middle.show_all()

def begin_drag( widget, data ):
	print "BEGINNING TO DRAG!"
	global dragging
	deselect_all()
	dragging = [False, None]

def end_drag( widget, data ):
	global dragging
	print "ENDED DRAG!"
	dragging = [False, None]

def start_drag( widget, drag_context, data, info, time ):
	print "STARTING TO DRAG!"
	global dragging
	
	dragging = [False, None]

	selected_path = widget.get_selected_items()[0]
	selected_iter = widget.get_model().get_iter(selected_path)

	# View the selected item, get the text, and map that to the proper image
	filename = get_icon_filename( \
		widget.get_model().get_value(selected_iter, 1) )

	data.set_text(filename, -1)


def keyboard_press( widget, data ):
	print "KEYBOARD PRESSED", widget
	key = data.keyval 
	if ( key == Gdk.KEY_Delete ):
		print 'DELETE KEY PRESS'
		for each in fixed_middle.get_children():
			if each.get_name() == 'selected':
				each.destroy()


fixed_middle.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
fixed_middle.connect("drag-data-received", received_drop )
fixed_middle.connect("drag-end", end_drag )

window.connect('key-press-event', keyboard_press)

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


def connect_to_server():
	print "Starting PowerShell..."
	powershell = Powershell()
	print "Importing PowerCLI..."
	powershell.import_powercli()
	print "Connecting to server..."
	powershell.connect_testing_server()


def load_vapps():

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