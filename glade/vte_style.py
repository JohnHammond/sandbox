#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib, Vte
import re
import time
import os
import glob


from powershell_engine import Powershell
builder = Gtk.Builder()
builder.add_from_file( 'vte_terminal.glade' )
builder.add_from_file( 'list.glade' )

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

		self.name = "New VM"
		self.hostname = 'virtual-machine'
		self.ip_method = 'static'
		self.ip_address = ''
		self.vapp_name = ''
		# self.ip_address = ''
		self.hdd = 50 # GB
		self.cpu = 1 # #
		self.ram = 2 # GB

		self.esxi_host = ''


class VMIcon():

	def __init__( self, image_filename):

		# Create the backend virtual machine object...
		self.vm = VM()
		self.vm.vapp_name = image_filename

		# Define the GUI controls...
		self.selected = False

		self.container = Gtk.EventBox()
		self.container.vmicon = self
		self.image_widget = Gtk.Image.new_from_file(image_filename)
		self.vbox_widget = Gtk.Box( orientation=Gtk.Orientation.VERTICAL )
		self.hbox_widget = Gtk.Box(  )
		self.entry_widget = Gtk.Entry()
		self.entry_widget.set_alignment(0.5)
		self.entry_widget.connect('changed', self.text_changed)

		# This is specifically for CSS styling...
		self.entry_widget.set_name('vmname_entry')

		self.entry_widget.set_text(self.vm.name)

		self.power_display = Gtk.Label()
		self.power_display.set_markup("<span font='15' color='black'> ⬛</span>")
		# self.power_display.set_markup("<span font='15' color='green'> ⬛</span>")
		# self.power_display.set_markup("<span font='15' color='darkred'> ⬛</span>")

		self.vbox_widget.pack_start(self.image_widget, True, True, 0)
		self.vbox_widget.pack_start(self.hbox_widget, True, True, 0)
		self.hbox_widget.pack_start(self.power_display, False, False, 0)
		self.hbox_widget.pack_start(self.entry_widget, True, True, 0)
		self.container.add(self.vbox_widget)

		self.container.connect('button-press-event', self.mouse_press)
		self.container.connect('button-release-event', self.mouse_release)

		# Create right click menu...
		self.right_click_menu = Gtk.Menu()
		self.power_on_button = Gtk.MenuItem("Power On")
		self.right_click_menu.append( self.power_on_button )
		self.power_on_button.connect('activate', self.power_on )
		self.power_off_button = Gtk.MenuItem("Power Off")
		self.right_click_menu.append( self.power_off_button )
		self.power_off_button.connect('activate', self.power_off )
		self.delete_vm_button = Gtk.MenuItem("Delete VM")
		self.right_click_menu.append( self.delete_vm_button )

		# Allow the user to move it in the display
		self.enable_drag_and_drop()

	def power_on( self, event = None ):
		command = "Start-VM '%s' -Confirm:$false" % self.vm.name

		def powered_on( output ):
			print output
			self.power_display.set_markup("<span font='15' color='green'> ⬛</span>")

		powershell.handle_command( command, powered_on )

	def power_off( self, event = None ):
		command = "Stop-VM '%s' -Confirm:$false" % self.vm.name

		def powered_off( output ):
			print output
			self.power_display.set_markup("<span font='15' color='red'> ⬛</span>")

		powershell.handle_command( command, powered_off )

	def set_processing( self ):
		self.container.set_name('processing')
		self.entry_widget.set_sensitive(False)


	def enable_drag_and_drop( self ):
		self.container.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], \
             DRAG_ACTION)
		self.container.drag_source_set_target_list(None)
		self.container.drag_source_add_text_targets()


	def text_changed( self, widget, data = None ):
		# print "VMICON TEXT CHANGED!"
		# print widget.get_text()
		self.vm.name = self.entry_widget.get_text()
		if self.selected:
			set_vm_name_display( self.vm.name )


	def mouse_press( self, widget, data ):
		global dragging
		print "VMICON IS CLICKED, ", widget

		if self.container.get_name() == 'processing':
			return
		
		# IF they right-click, show a menu!
		if data.button == 3:
			if self.selected:
				self.right_click_menu.show_all()
				self.right_click_menu.popup(None,None,None,None,0, \
										Gtk.get_current_event_time())

		# Double-click with left-click...
		if data.type == Gdk.EventType._2BUTTON_PRESS and data.button == 1:
			print "*** DOUBLE CLICKED! ***"
			powershell.run_command( \
				'Start-Process chromium-browser (../get_html_link.ps1 -VMName "%s")' % self.vm.name )
		

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
		create_button.show()
		provision_button.show()

		hostname_entry.set_sensitive(True)
		ip_address_entry.set_sensitive(static_radio_button.get_active())
		hdd_spin_button.set_sensitive(True)
		cpu_spin_button.set_sensitive(True)
		ram_spin_button.set_sensitive(True)
		esxi_hosts_combo_box.set_sensitive(True)

	def unselect( self ):
		global dragging

		self.selected = False
		deselect_all()
		self.container.set_name('nothing')
		create_button.hide()

		hostname_entry.set_sensitive(False)
		ip_address_entry.set_sensitive(False)
		hdd_spin_button.set_sensitive(False)
		cpu_spin_button.set_sensitive(False)
		ram_spin_button.set_sensitive(False)
		esxi_hosts_combo_box.set_sensitive(False)


	def mouse_release( self, widget, data ):
		
		global dragging
		print "VMICON IS RELEASED, ", widget
		deselect_all()
		self.container.set_name('selected')
		
		dragging = [False, None]


class PowerShellWidget():

	def __init__( self, text_view_widget, text_entry_widget, scroller ):

		# Set the appropriate GTK widgets...
		self.output_widget = text_view_widget
		self.input_widget = text_entry_widget
		self.scroller = scroller

		# Set automatic scrolling
		self.output_widget.connect( 'size-allocate', self.automatic_scroll )

		# Connect the command input box
		self.input_widget.connect('activate', self.enter_command)


		# Create the background process.
		self.powershell = Powershell()

		# Get the focus!
		self.focus()


	def focus( self, widget = None, data = None ):
		self.input_widget.grab_focus()

	def automatic_scroll( self, widget, data = None ):
		# Scroll the window to the bottom.
		adj = self.scroller.get_vadjustment()
		adj.set_value( adj.get_upper() - adj.get_page_size() )

	def run_command( self, command ):
		'''
		This is the BACKEND process of actually running the command. 
		It handles giving the output to the display widget,
		'''
		self.input_widget.set_text(command)
		self.input_widget.select_region(0,-1)
		output = self.powershell.run_command( command )
		
		# Get to the end of the output... and then place the new output!
		self.output_widget.get_buffer().place_cursor( \
			self.output_widget.get_buffer().get_end_iter() )
		self.output_widget.get_buffer().insert_at_cursor( \
			"PS> " + command + "\n" + output + "\n\n" )

	def enter_command( self, widget, data =None ):
		'''
		This is the FRONTEND process for typing in a command on the GUI.
		It just passes it to the backend function.
		'''
		self.run_command( widget.get_text() )

horizontal_scroll = 0
vertical_scroll = 0


def do_nothing(anything = None, signal_handler = 0):
	pass

class VteWidget:

	def __init__( self, container): 

		# Some example code...
		# https://www.programcreek.com/python/example/56624/vte.Terminal

		# This is the  GTK Widget. It only runs on Linux/Mac unfortunately...
		self.terminal = Vte.Terminal()

		# Set colors...
		self.terminal.set_color_foreground(Gdk.RGBA(0,0,0,255))
		self.terminal.set_color_background(Gdk.RGBA(0.8, 0.8, 0.8, 1.0))

		# This is the path to the shell. May need changed for os-specific work
		self.command = '/usr/bin/powershell'

		# Stitch the shell to the widget...
		self.terminal.spawn_sync(
			Vte.PtyFlags.DEFAULT, #default is fine
			#os.environ['HOME'], #where to start the command?
			os.getcwd(),
			[ self.command ], #where is the emulator?
			[], #it's ok to leave this list empty
			GLib.SpawnFlags.DO_NOT_REAP_CHILD,
			None, #at least None is required
			None,
		)

		# Keep track fo command output in a variable
		self.last_handle_id = 0
		self.last_output = ''
		self.visible_output = ''


		# Add it to the container (assuming it is a GtkBox...)
		self.box = container
		self.box.pack_start(self.terminal, True, True, 0)

		# Keep track of the function being used to process output.
		# THIS IS NECESSARY FOR OUR SYNCHRONIZED I/O!
		self.handling_output_function = None
		self.initialized = False

		# Monitor when a command finishes...
		# THIS IS NECESSARY FOR OUR SYNCHRONIZED I/O!
		self.terminal.connect('contents-changed', self.get_output,
			self.handling_output_function)

		# Startup...
		#GLib.timeout_add_seconds( 2, self.initialize_powershell )

	def run_command( self, command ):
		# If PowerShell is in a spot to receive output...
		if self.terminal.get_sensitive():
			
			self.terminal.feed_child(command + '\n', len(command)+ 1)




	def get_output( self, widget, handling_output_function = None ):
		'''
		Whenever the display changes in the terminal, monitor the changes
		so we can scrape out the output of a command.
		'''
		self.visible_output = self.terminal.get_text()[0]
		if self.visible_output.endswith('> \n\n\n\n\n') \
												and not self.initialized:
			self.initialized = True
			GLib.timeout_add(800, self.initialize)
			# self.initialize()

		# If we have set up a handler function, carve out the last output.
		if self.handling_output_function:
			command_output = \
		"\n".join(self.visible_output.split('> ')[-1].split('\n')[1:]).strip()
			
			# If there is output, handle it once, and then drop the handler.
			# THIS CONDITION IS NECESSARY BECAUSE THE SIGNAL FIRES A LOT
			if command_output:
				self.terminal.set_sensitive(True)
				self.handling_output_function(command_output)
				left_spinner.stop()
				self.handling_output_function = None


	def handle_command( self, command, handling_output_function = None ):
		'''
		This function runs a specific command with a specified function
		to handle the output of the command once it is returned.
		'''
		self.handling_output_function = handling_output_function
		self.run_command('clear')
		self.run_command(command)
		left_spinner.start()

		if self.handling_output_function != None:
			self.terminal.set_sensitive(False)


	def import_powercli( self ):

		self.run_command('# Importing PowerCLI...')
		self.run_command('Get-Module -ListAvailable PowerCLI* | Import-Module')


	def connect_server( self ):
		self.run_command('# Connecting to vCenter server...')
		self.run_command('Connect-VIServer 10.1.214.223 -User administrator@vsphere.local -Password S@ndbox2')

	# I put these optional parameters in case it is called by a widget handler
	def load_vapps( self, widget = None, data = None ):

		# Disable the button so they can't click it again...
		load_vapps_button.set_sensitive(False)
		self.run_command('# Loading vApps...')
		self.handle_command(\
'(Get-ChildItem vmstore:/sandbox_datacenter/datastore1/vapps).Name -Join ",,"',
	self._load_vapps)

	def _load_vapps( self, vapps ):
		# for vapp in vapps.split('@'):
		# 	print vapp

		# Cut out the Parentheses...
		vapps_list = vapps.split(',,')
		# vapps_list = \
		# 	[ re.sub(r'\s*\(.*\)\s*','',vapp) for vapp in vapps.split(',,') ] 

		for vapp in vapps_list:
			original_vapp_string = vapp
			#vapp = re.sub(r'\s*\(.*\)\s*','',vapp)
			added = False
			for key in mapping:
				if key in vapp.lower():
					widget_image = GdkPixbuf.Pixbuf.new_from_file( mapping[key][0] )
					# widget_image.vapp_string = original_vapp_string
					mapping[key][1].get_model().append(
						[widget_image, vapp ])
					
					added = True
					break
			if not added:
				windows_icons.get_model().append(
					[GdkPixbuf.Pixbuf.new_from_file( \
						"icons/anything_150x150.png" ), vapp ])

		load_vapps_button.hide()

	def initialize( self ):
		self.initialized = True
		self.import_powercli()
		self.connect_server()

		# assuming we connect okay...
		self.handle_command("# Connected! Welcome to SANDBOX!", load_vapps_button.set_sensitive)

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
ip_address_entry = builder.get_object('ip_address_entry')
esxi_hosts_combo_box = builder.get_object('esxi_hosts_combo_box')
hdd_spin_button = builder.get_object('hdd_spin_button')
cpu_spin_button = builder.get_object('cpu_spin_button')
ram_spin_button = builder.get_object('ram_spin_button')
fixed_middle_event_box = builder.get_object('fixed_middle_event_box')
windows_icons = builder.get_object('windows_icons')
linux_icons = builder.get_object('linux_icons')
ics_icons = builder.get_object('ics_icons')
middle_scroll = builder.get_object('middle_scroll')
create_button = builder.get_object('create_button')
left_spinner = builder.get_object('left_spinner')
provision_window = builder.get_object('provision_window')
provision_button = builder.get_object('provision_button')
configure_button = builder.get_object('configure_button')
static_radio_button = builder.get_object('static_radio_button')


hostname_entry.set_sensitive(False)
ip_address_entry.set_sensitive(False)
hdd_spin_button.set_sensitive(False)
cpu_spin_button.set_sensitive(False)
ram_spin_button.set_sensitive(False)
esxi_hosts_combo_box.set_sensitive(False)




def on_enabled_toggle_toggled( widget, path ):
	global provisioning_features

	provisioning_features[path][1] = not provisioning_features[path][1]


def ok_button_activate_cb( widget ):
	global provisioning_features, scripts
	provision_window.hide()

	item = provisioning_features.get_iter_first()

	while ( item != None ):
		script_name = provisioning_features[item][0]
		enabled = provisioning_features[item][1]

		if enabled:
			command = '%s -VMName "%s"' % \
					( scripts[script_name], 
					get_selected_vmicon().vm.name )

			powershell.handle_command( command ) 

		item = provisioning_features.iter_next(item)




def close_window(widget):
	Gtk.main_quit()

def on_provision_button_clicked( widget = None, data = None ):
	provision_window.show_all()

def setting_ip_address(output):
	configure_button.set_sensitive(True)

def setting_vm_specs( output ):
	pass


def on_configure_button_clicked( widget = None, data = None ):
	print get_selected_vmicon().vm.name
	print "HDD", hdd_spin_button.get_value()
	print "CPU", cpu_spin_button.get_value()
	print "RAM", ram_spin_button.get_value()

	command = "../powercli/configure_vm.ps1 " +\
		  " -VMName \"" + 	get_selected_vmicon().vm.name + "\"" +\
		  " -VMCPU " + str(cpu_spin_button.get_value()) + \
		  " -VMMemory " + str(ram_spin_button.get_value()) + \
		  " -IPAddress \"" + ip_address_entry.get_text() + "\""

	powershell.handle_command(command, setting_ip_address ) 

	configure_button.set_sensitive(True)

def on_static_radio_button_toggled( widget = None, eventt = None ):
	ip_address_entry.set_sensitive(static_radio_button.get_active())

def provision_cancel_button_clicked(widget = None, eventt = None):
	provision_window.hide()


handlers = {
	"on_enabled_toggle_toggled": on_enabled_toggle_toggled,
	"ok_button_activate_cb": ok_button_activate_cb,
	"provision_cancel_button_clicked": provision_cancel_button_clicked,
	"on_provision_button_clicked": on_provision_button_clicked,
	"on_configure_button_clicked": on_configure_button_clicked,
	"on_static_radio_button_toggled": on_static_radio_button_toggled,
}

builder.connect_signals(handlers)
provisioning_features = builder.get_object('provisioning_features')
provisioning_treeview = builder.get_object('provisioning_treeview')

bottom_vbox = builder.get_object('bottom_vbox')
powershell = VteWidget(bottom_vbox)
load_vapps_button = builder.get_object('load_vapps_button')
load_vapps_button.connect('clicked', powershell.load_vapps)
load_vapps_button.set_sensitive(False)

def hostname_entry_changed( widget, data = None ):
	print "HOSTNAME ENTRY CLICKED"
	children = fixed_middle.get_children()
	for eventbox in children:
		if ( eventbox.get_name() == 'selected' ):
			print eventbox.vmicon

hostname_entry.connect('changed', hostname_entry_changed)

def deselect_all():
	for each in fixed_middle.get_children(): 
		if each.get_name() == 'selected':
			each.set_name('normal')

'''
# This is an example handler for our command output.
# It just takes an argument, which is a string of the output being supplied
# You can do whatever you want with it, but it must take in a variable

def handle_command_output( output ):	
	print output.upper()
'''

def get_selected_vmicon():

	for child in fixed_middle.get_children():
		if (  child.get_name() == 'selected' ):
			return child.vmicon

def middle_pressed( widget, data ): pass
def middle_released( widget, data ): pass
	# get_selected_vmicon().unselect()


fixed_middle.connect('scroll-event', scroll_event)
fixed_middle_event_box.connect('button-press-event', middle_pressed)
fixed_middle_event_box.connect('button-release-event', middle_released)
middle_scroll.get_hscrollbar().connect('change-value', h_scrollbar_event)
middle_scroll.get_vscrollbar().connect('change-value', v_scrollbar_event)

mapping = {
	"windows 10": [ "icons/windows_10_150x150.png", windows_icons],
	"centos": [ "icons/centos_150x150.png", linux_icons],
	"samurai": [ "icons/samurai_150x150.png", ics_icons],
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

	filename, vapp_name = data.get_text().split('<DELIMETER>')

	vmicon = VMIcon( filename )
	vmicon.vm.vapp_name = vapp_name
	print "**** SET VAPP NAME TO", vmicon.vm.vapp_name
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
	
	if widget.get_name() == 'processing':
		return

	dragging = [False, None]

	selected_path = widget.get_selected_items()[0]
	selected_iter = widget.get_model().get_iter(selected_path)
	
	gtk_image =  widget.get_model().get_value(selected_iter, 0)
	vapp_name = widget.get_model().get_value(selected_iter, 1)
	# View the selected item, get the text, and map that to the proper image
	filename = get_icon_filename( vapp_name )

	data.set_text("<DELIMETER>".join([ filename, vapp_name ]), -1)



def keyboard_press( widget, data ):
	print "KEYBOARD PRESSED", widget
	get_selected_vmicon()
	key = data.keyval 
	if ( key == Gdk.KEY_Delete ):
		print 'DELETE KEY PRESS'
		for each in fixed_middle.get_children():
			if each.get_name() == 'selected':
				each.destroy()


def finished_creating_vm( output ):
	powershell.run_command('Get-VM')

	create_button.hide()
	
	configure_button.show()

def create_virtual_machine( widget, data = None ):
	vmicon = get_selected_vmicon()

	if vmicon:

		ovf_location = \
	'/media/john/C24CE0124CDFFED3/Users/Capstone/local_vapps/%s/*.ovf' % vmicon.vm.vapp_name

		powershell.handle_command('../powercli/create_vm_from_vapp.ps1 -VMName "' +\
		vmicon.vm.name + '" -OVFLocation "' + ovf_location + '" ', finished_creating_vm  )
		vmicon.set_processing()
		
		create_button.set_sensitive(False)

	else:
		print "NO VMICON IS SELECTED!!!!!!!!!!"


create_button.connect('clicked', create_virtual_machine)


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

window.show_all()
window.connect('destroy', Gtk.main_quit)
create_button.hide()
provision_button.hide()
left_spinner.start()


scripts = \
	{ os.path.splitext(os.path.basename(x))[0].title().replace('_'," "):x \
	for x in glob.glob("../powercli/provision/*.ps1")}

for key in scripts.iterkeys():
	provisioning_features.append([ key, False] )



Gtk.main()

