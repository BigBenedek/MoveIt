
# GUI application for ClickNCommand
import tkinter as tk
from tkinter import ttk

# The file where the keyboard and mouse events are handled
import clickanput as can

# Handle cleanup on exit
import atexit

import json

import tkinter.filedialog as filedialog
from Click import Click
import pyautogui

save_file_name = 'test.json'

# Callback for window close event
def on_closing():
    """Called when the window is closed"""
    print("Closing application...")
    can.stop_listeners()
    root.destroy()

# Start replay in a separate thread
def start_replay():
    """Start replay in a separate thread"""
    # Avoid starting multiple replay threads
    if getattr(can, 'replaying', False):
        print("Replay already running")
        return

    can.replaying = True
    import threading
    replay_thread = threading.Thread(target=can.replay_clicks)
    replay_thread.daemon = True
    replay_thread.start()

# Stop the current replay
def stop_replay():
    """Stop the current replay"""
    can.replaying = False
    print("Replay stopped")

# Callback for spinbox value changes
def update_step_time():
    """Update the step time when spinbox value changes"""
    global step_time_var
    try:
        new_time = float(step_time_var.get())
        can.replay_step_time = new_time  # Update the value in clickanput module
        can.pyautogui.PAUSE = new_time  # Update the pause in pyautogui
        #print(f"Step time updated to: {new_time} seconds")
    except ValueError:
        print("Invalid step time value")

# Callback for spinbox value changes needed a different function
def on_spinbox_change(*args):
    """Called when spinbox value changes"""
    update_step_time()

# Get the absolute screen position and size of a button
def get_button_position(button_widget):
    """Get the absolute screen position and size of a button"""
    global root
    # Update the widget to ensure geometry is calculated
    button_widget.update_idletasks()
    
    # Get button position relative to root window
    x = button_widget.winfo_x()
    y = button_widget.winfo_y()
    
    # Get root window position on screen
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    
    # Calculate absolute screen position
    abs_x = root_x + x
    abs_y = root_y + y
    
    # Get button size
    width = button_widget.winfo_width()
    height = button_widget.winfo_height()
    
    return abs_x, abs_y, width, height

# Register button exclusions to avoid recording clicks on own gui buttons
def register_button_exclusions():
    """Register all buttons to be excluded from recording"""
    global record_button, start_replay_button, stop_replay_button, clear_button
    try:
        # Clear existing exclusions
        can.clear_button_exclusions()
        
        # Get positions for all buttons that should be excluded
        buttons_to_exclude = [record_button, start_replay_button, stop_replay_button, clear_button]
        
        for button in buttons_to_exclude:
            if button.winfo_exists():
                x, y, w, h = get_button_position(button)
                can.add_button_exclusion(x, y, w, h)
    except Exception as e:
        print(f"Error registering button exclusions: {e}")

def on_window_configure(event):
    """Called when window is moved or resized"""
    global root
    if event.widget == root:  # Only respond to root window events
        # Small delay to ensure geometry is updated
        root.after(100, register_button_exclusions)

# Save recorded clicks to a JSON file
def save_recorded_clicks():
    """Save recorded clicks to a JSON file"""
    global can, save_file_name

    # Convert Click objects to dictionaries
    click_data = [click_obj.to_dict() for click_obj in can.click_positions]
   
    with open(save_file_name, 'w+') as f:
        json.dump(click_data, f, indent=2)
    print(f"Recorded clicks saved to {save_file_name}")


# Load recorded clicks from a JSON file
def load_recorded_clicks():
    """Load recorded clicks from a JSON file"""
    global can, save_file_name
    save_file_name = filedialog.askopenfilename(defaultextension=".json", initialdir=".",
                                                   filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    
    with open(save_file_name, 'r') as f:
        click_data = json.load(f)
    
    # Convert dictionaries back to Click objects
    can.click_positions = [Click.from_dict(data) for data in click_data]
    print(f"Loaded {len(can.click_positions)} recorded clicks from {save_file_name}")
    

# Initialize the main application window
root = tk.Tk()
root.title("ClickNCommand")
root.configure(bg="lightblue")
root.minsize(800, 700)
root.maxsize(1200, 900)
root.geometry("900x800+50+50")

# Don't start listeners by default - user will control them with buttons

# Set up window close handler
root.protocol("WM_DELETE_WINDOW", on_closing)
atexit.register(can.stop_listeners)

# Bind window configure event to update button positions
root.bind('<Configure>', on_window_configure)

# Schedule initial button registration after GUI is fully loaded
root.after(500, register_button_exclusions)

# Auto-start keyboard listener so hotkeys work immediately (toggleable from GUI)
try:
    can.start_keyboard_listener()
except Exception as e:
    print(f"Could not start keyboard listener automatically: {e}")

# Keyboard listener controls
listener_frame = tk.Frame(root, bg="lightblue")
listener_frame.pack(pady=10)

tk.Label(listener_frame, text="Keyboard Listener Control:", bg="lightblue", font=("Arial", 10, "bold")).pack()

def start_keyboard_listener():
    """Start keyboard listener for hotkeys"""
    can.start_keyboard_listener()

def stop_keyboard_listener():
    """Stop keyboard listener"""
    can.stop_keyboard_listener()

listener_buttons_frame = tk.Frame(listener_frame, bg="lightblue")
listener_buttons_frame.pack(pady=5)

start_listener_button = tk.Button(listener_buttons_frame, text="Start Keyboard Listener", 
                                 command=start_keyboard_listener, width=20)
start_listener_button.pack(side=tk.LEFT, padx=5)

stop_listener_button = tk.Button(listener_buttons_frame, text="Stop Keyboard Listener", 
                                command=stop_keyboard_listener, width=20)
stop_listener_button.pack(side=tk.LEFT, padx=5)

tk.Label(listener_frame, text="Hotkeys work only when keyboard listener is active:", bg="lightblue").pack(pady=2)
tk.Label(listener_frame, text="'d' = toggle recording | 'y' = toggle replay | 'c' = clear | 'q' = stop recording | 'Q' = exit", 
         bg="lightblue", font=("Arial", 8)).pack(pady=2)

# GUI Elements
tk.Label(root, text="Toggle recording clicks", bg="lightblue").pack(pady=5)
record_button = tk.Button(root, text="Record", command=can.recording_switch, width=20)
record_button.pack(pady=2)

# Record button
tk.Label(root, text="Toggle replaying recorded clicks", bg="lightblue").pack(pady=5)
replay_frame = tk.Frame(root, bg="lightblue")
replay_frame.pack(pady=2)

# Replay buttons
start_replay_button = tk.Button(replay_frame, text="Start Replay", command=start_replay, width=15)
start_replay_button.pack(side=tk.LEFT, padx=2)
stop_replay_button = tk.Button(replay_frame, text="Stop Replay", command=stop_replay, width=15)
stop_replay_button.pack(side=tk.LEFT, padx=2)

# Step time controls
step_time_frame = tk.Frame(root, bg="lightblue")
step_time_frame.pack(pady=5)

tk.Label(step_time_frame, text="Step Time (seconds):", bg="lightblue").pack(side=tk.LEFT, padx=2)

# Create StringVar to track spinbox changes
step_time_var = tk.StringVar(value="0.1")
step_time_var.trace_add('write', on_spinbox_change)  # Track changes to the variable

step_time_spinbox = tk.Spinbox(step_time_frame, from_=0.001, to=10.0, increment=0.001, textvariable=step_time_var, width=8)

# Update when focus leaves the spinbox
step_time_spinbox.bind('<FocusOut>', lambda event: on_spinbox_change())

# Bind Enter key to update when typing
step_time_spinbox.bind('<Return>', lambda event: on_spinbox_change())
step_time_spinbox.pack(side=tk.LEFT, padx=2)

# Initialize the step time in clickanput module
can.replay_step_time = 0.1

# Click editing table
click_table_frame = tk.Frame(root, bg="lightblue")
click_table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

tk.Label(click_table_frame, text="Click Editor - Edit individual clicks:", bg="lightblue", font=("Arial", 10, "bold")).pack(pady=5)


# Create Treeview for click editing (added per-row Scroll column)
columns = ('index', 'x', 'y', 'delay', 'offset_x', 'offset_y', 'scroll', 'double_click')
click_tree = ttk.Treeview(click_table_frame, columns=columns, show='headings', height=6)

# Define column headings
click_tree.heading('index', text='#')
click_tree.heading('x', text='X')
click_tree.heading('y', text='Y')
click_tree.heading('delay', text='Delay (s)')
click_tree.heading('offset_x', text='Offset X')
click_tree.heading('offset_y', text='Offset Y')
click_tree.heading('scroll', text='Scroll')
click_tree.heading('double_click', text='Double Click')

# Define column widths
click_tree.column('index', width=40, anchor='center')
click_tree.column('x', width=80, anchor='center')
click_tree.column('y', width=80, anchor='center')
click_tree.column('delay', width=100, anchor='center')
click_tree.column('offset_x', width=80, anchor='center')
click_tree.column('offset_y', width=80, anchor='center')
click_tree.column('scroll', width=80, anchor='center')
click_tree.column('double_click', width=100, anchor='center')

click_tree.pack(fill=tk.BOTH, expand=True)

# Scrollbar for the treeview
scrollbar = ttk.Scrollbar(click_table_frame, orient=tk.VERTICAL, command=click_tree.yview)
click_tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Function to refresh the click table
def refresh_click_table():
    """Refresh the click table with current click positions"""
    # Clear existing items
    for item in click_tree.get_children():
        click_tree.delete(item)
    
    # Add current clicks
    for i, click_obj in enumerate(can.click_positions):
        # Show scroll amount in its own column; double-click column shows Yes/No
        scroll_val = click_obj.scroll_amount if getattr(click_obj, 'is_scroll', False) else 0
        click_tree.insert('', tk.END, values=(
            i+1,
            click_obj.x,
            click_obj.y,
            click_obj.delay,
            click_obj.offset_x,
            click_obj.offset_y,
            scroll_val,
            'Yes' if click_obj.is_double_click else 'No'
        ))

# Function to handle cell editing
def on_tree_double_click(event):
    """Handle double-click on treeview to edit cell"""
    region = click_tree.identify_region(event.x, event.y)
    if region != 'cell':
        return
    
    column = click_tree.identify_column(event.x)
    row = click_tree.identify_row(event.y)
    
    if not row or not column:
        return
    
    # Get column index
    col_index = int(column[1:]) - 1  # ttk columns are 1-indexed
    
    # Get current value
    item = click_tree.item(row)
    current_value = item['values'][col_index]
    
    # Create entry widget for editing
    x, y, width, height = click_tree.bbox(row, column)
    
    # Create entry
    entry = tk.Entry(click_table_frame)
    entry.place(x=x, y=y, width=width, height=height)
    entry.insert(0, str(current_value))
    entry.focus()
    
    def save_edit():
        """Save the edited value"""
        new_value = entry.get()
        try:
            # Validate and convert value based on column
            if col_index in [1, 2, 4, 5, 6]:  # X, Y, Offset X, Offset Y, Scroll - integers
                # Allow user to type "Scroll 100" in scroll column; parse that
                s = str(new_value).strip()
                if s.lower().startswith('scroll'):
                    parts = s.replace(':', ' ').split()
                    amount = 0
                    for p in parts:
                        try:
                            amount = int(p)
                            break
                        except ValueError:
                            continue
                    new_value = int(amount)
                else:
                    new_value = int(float(s))
            elif col_index == 3:  # Delay - float
                new_value = float(new_value)
            elif col_index == 7:  # Double click - boolean
                nv = str(new_value).strip()
                new_value_bool = nv.lower() in ('yes', 'true', '1', 'y')
                new_value = 'Yes' if new_value_bool else 'No'
            
            # Update the values list
            values = list(item['values'])
            values[col_index] = new_value
            click_tree.item(row, values=values)
            
            # Update the actual Click object
            click_index = int(values[0]) - 1
            if 0 <= click_index < len(can.click_positions):
                click_obj = can.click_positions[click_index]
                if col_index == 1:  # X
                    click_obj.x = int(new_value)
                elif col_index == 2:  # Y
                    click_obj.y = int(new_value)
                elif col_index == 3:  # Delay
                    click_obj.delay = float(new_value)
                elif col_index == 4:  # Offset X
                    click_obj.offset_x = int(new_value)
                elif col_index == 5:  # Offset Y
                    click_obj.offset_y = int(new_value)
                elif col_index == 6:  # Scroll amount
                    click_obj.scroll_amount = int(new_value)
                    click_obj.is_scroll = (int(new_value) != 0)
                elif col_index == 7:  # Double click
                    click_obj.is_scroll = False
                    click_obj.is_double_click = (new_value == 'Yes')
            
            print(f"Updated click {click_index + 1}: {values}")
            
        except ValueError as e:
            print(f"Invalid value: {e}")
        
        entry.destroy()
    
    def cancel_edit(event=None):
        """Cancel the edit"""
        entry.destroy()
    
    entry.bind('<Return>', lambda e: save_edit())
    entry.bind('<Escape>', cancel_edit)
    entry.bind('<FocusOut>', lambda e: save_edit())

# Bind double-click event to treeview
click_tree.bind('<Double-1>', on_tree_double_click)

# Button to refresh table
refresh_table_button = tk.Button(click_table_frame, text="Refresh Table", command=refresh_click_table, width=15)
refresh_table_button.pack(pady=5)

# Scroll-action controls: amount + add button
scroll_control_frame = tk.Frame(click_table_frame, bg="lightblue")
scroll_control_frame.pack(pady=4)

tk.Label(scroll_control_frame, text="Scroll amount:", bg="lightblue").pack(side=tk.LEFT, padx=2)
scroll_amount_var = tk.StringVar(value="100")
scroll_amount_spinbox = tk.Spinbox(scroll_control_frame, from_=-1000, to=1000, increment=1, textvariable=scroll_amount_var, width=8)
scroll_amount_spinbox.pack(side=tk.LEFT, padx=2)

def add_scroll_at_cursor():
    """Add a scroll action at current cursor position to the click list"""
    try:
        amount = int(scroll_amount_var.get())
    except ValueError:
        print("Invalid scroll amount")
        return

    try:
        mx, my = pyautogui.position()
    except Exception as e:
        print(f"Could not get mouse position: {e}")
        return

    scroll_click = Click(x=mx, y=my, delay=0, is_double_click=False, offset_x=0, offset_y=0, is_scroll=True, scroll_amount=amount)
    can.click_positions.append(scroll_click)
    print(f"Added scroll action at ({mx},{my}) amount={amount}")
    refresh_click_table()

add_scroll_button = tk.Button(scroll_control_frame, text="Add Scroll at Cursor", command=add_scroll_at_cursor)
add_scroll_button.pack(side=tk.LEFT, padx=6)

# Clear clickpoints button
tk.Label(root, text="Clear recorded clicks", bg="lightblue").pack(pady=5)
clear_button = tk.Button(root, text="Clear clickpoints", command=can.clear_clicks, width=20)
clear_button.pack(pady=2)

# Status display
status_frame = tk.Frame(root, bg="lightblue")
status_frame.pack(pady=10)
tk.Label(status_frame, text="Status:", bg="lightblue", font=("Arial", 10, "bold")).pack()

# Function to update status display at bottom
def update_status():
    """Update status display"""
    # Check if listeners are running
    kb_running = can.key_listener and can.key_listener.running
    mouse_running = can.mouse_listener and can.mouse_listener.running
    
    # Get current mouse position
    try:
        mouse_x, mouse_y = pyautogui.position()
        mouse_pos_text = f" | Mouse: ({mouse_x}, {mouse_y})"
    except Exception as e:
        mouse_pos_text = " | Mouse: N/A"
    
    status_text = f"Recording: {'ON' if can.recording else 'OFF'} | "
    status_text += f"Replaying: {'ON' if can.replaying else 'OFF'} | "
    status_text += f"Clicks recorded: {len(can.click_positions)} | "
    status_text += f"Button exclusions: {len(can.button_exclusions)} | "
    status_text += f"Keyboard Listener: {'ON' if kb_running else 'OFF'} | "
    status_text += f"Mouse Listener: {'ON' if mouse_running else 'OFF'}"
    status_text += mouse_pos_text
    
    if hasattr(update_status, 'status_label'):
        update_status.status_label.config(text=status_text)
    else:
        update_status.status_label = tk.Label(status_frame, text=status_text, bg="lightblue", font=("Arial", 9))
        update_status.status_label.pack()
    
    # Auto-refresh click table when clicks change
    if hasattr(update_status, 'last_click_count'):
        if update_status.last_click_count != len(can.click_positions):
            refresh_click_table()
    else:
        refresh_click_table()
    
    update_status.last_click_count = len(can.click_positions)
    
    # Schedule next update (ms)
    root.after(100, update_status)  # Faster update for mouse position

# Start status updates
update_status()

save_n_load_frame = tk.Frame(root, bg="lightblue")
save_n_load_frame.pack(pady=10)

tk.Label(save_n_load_frame, text="Saved file's name: ", bg="lightblue").pack(side=tk.LEFT, padx=5)
save_file_name_label = tk.Label(save_n_load_frame, text=save_file_name, bg="lightblue")
save_file_name_label.pack(side=tk.LEFT, padx=5)

def on_file_name_change():
    """Update the save file name when entry changes"""
    global save_file_name, file_name_entry_var, save_file_name_label
    save_file_name = file_name_entry_var.get().strip()
    if len(save_file_name) > 20:
        return
    if not save_file_name.endswith('.json'):
        save_file_name += '.json'
    if save_file_name_label:
        save_file_name_label.config(text=save_file_name)
    #print(f"Save file name updated to: {save_file_name}")

def on_file_name_entry_change(*args):
    """Callback for file name entry changes"""
    on_file_name_change()

file_name_entry_var = tk.StringVar(value=save_file_name)
file_name_entry_var.trace_add('write', on_file_name_entry_change) 

file_name_entry_var.set(save_file_name)
file_name_entry = tk.Entry(save_n_load_frame, textvariable=file_name_entry_var, width=30)
file_name_entry.pack(side=tk.LEFT, padx=5)

file_name_entry.bind('<FocusOut>', lambda event: on_file_name_change())

# Bind Enter key to update when typing
file_name_entry.bind('<Return>', lambda event: on_file_name_change())





save_clicks_button = tk.Button(save_n_load_frame, text="Save Recorded Clicks", command=save_recorded_clicks, width=20)
save_clicks_button.pack()

load_clicks_button = tk.Button(save_n_load_frame, text="Load Recorded Clicks", command=load_recorded_clicks, width=20)
load_clicks_button.pack()

# Start the main event loop it is for the GUI window to start and initialize
root.mainloop()