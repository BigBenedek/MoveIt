
# GUI application for ClickNCommand
import tkinter as tk

# The file where the keyboard and mouse events are handled
import clickanput as can

# Handle cleanup on exit
import atexit

import json

import tkinter.filedialog as filedialog

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

   
    with open(save_file_name, 'w+') as f:
        json.dump(can.click_positions, f)
    print(f"Recorded clicks saved to {save_file_name}")


# Load recorded clicks from a JSON file
def load_recorded_clicks():
    """Load recorded clicks from a JSON file"""
    global can, save_file_name
    save_file_name = filedialog.askopenfilename(defaultextension=".json", initialdir=".",
                                                   filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    
    with open(save_file_name, 'r') as f:
        can.click_positions = json.load(f)
    print(f"Loaded {len(can.click_positions)} recorded clicks from {save_file_name}")
    

# Initialize the main application window
root = tk.Tk()
root.title("ClickNCommand")
root.configure(bg="lightblue")
root.minsize(700, 500)
root.maxsize(700, 500)
root.geometry("600x600+50+50")

# Don't start listeners by default - user will control them with buttons

# Set up window close handler
root.protocol("WM_DELETE_WINDOW", on_closing)
atexit.register(can.stop_listeners)

# Bind window configure event to update button positions
root.bind('<Configure>', on_window_configure)

# Schedule initial button registration after GUI is fully loaded
root.after(500, register_button_exclusions)

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
    
    status_text = f"Recording: {'ON' if can.recording else 'OFF'} | "
    status_text += f"Replaying: {'ON' if can.replaying else 'OFF'} | "
    status_text += f"Clicks recorded: {len(can.click_positions)} | "
    status_text += f"Button exclusions: {len(can.button_exclusions)} | "
    status_text += f"Keyboard Listener: {'ON' if kb_running else 'OFF'} | "
    status_text += f"Mouse Listener: {'ON' if mouse_running else 'OFF'}"
    
    if hasattr(update_status, 'status_label'):
        update_status.status_label.config(text=status_text)
    else:
        update_status.status_label = tk.Label(status_frame, text=status_text, bg="lightblue", font=("Arial", 9))
        update_status.status_label.pack()
    
    # Schedule next update (ms)
    root.after(500, update_status)

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