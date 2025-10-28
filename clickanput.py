import pynput.mouse as mouse
import pynput.keyboard as keyboard
import pyautogui
import time
import threading
from Click import Click


recording = False
replaying = False
click_positions = []  # Store click positions as a dictionary

key_listener = None
mouse_listener = None
button_exclusions = []  # Store button positions to exclude from recording
replay_step_time = 0.1  # Configurable step time for replay


def on_click(x, y, button, pressed):
    global recording, replaying, click_positions, button_exclusions
    if button == mouse.Button.left and pressed and recording:
        # Check if click is within any excluded button area
        if is_click_on_button(x, y):
            return

        # Check for double click (rapid clicks at same position)
        double_click = False
        if (click_positions and
            x == click_positions[-1].x and
            y == click_positions[-1].y and
            not click_positions[-1].is_double_click):
            # Convert last click to double click
            click_positions[-1].is_double_click = True
            return

        # Create new click
        click = Click(x, y, button=button.name, delay=0, is_double_click=double_click)
        click_positions.append(click)
        print(f"Recorded click at: ({x}, {y})")
        

def is_click_on_button(x, y):
    """Check if the click coordinates are within any excluded button area"""
    global button_exclusions
    for button_info in button_exclusions:
        bx, by, bw, bh = button_info
        if bx <= x <= bx + bw and by <= y <= by + bh:
            return True
    return False

def add_button_exclusion(x, y, width, height):
    """Add a button area to exclude from recording"""
    global button_exclusions
    button_exclusions.append((x, y, width, height))
    #print(f"Added button exclusion: x={x}, y={y}, w={width}, h={height}")

def clear_button_exclusions():
    """Clear all button exclusions"""
    global button_exclusions
    button_exclusions = []
    #print("Recalculated all button exclusions")

def on_press(key):
    global recording, replaying, click_positions
    try:
        if key == keyboard.KeyCode.from_char('q') and recording:
            print("Stopped recording...")
            recording = False
            # Stop mouse listener when recording stops via keyboard
            global mouse_listener
            if mouse_listener and mouse_listener.running:
                mouse_listener.stop()
                print("Mouse listener stopped")
        
        elif key == keyboard.KeyCode.from_char('Q'):
            print("Exiting listeners.")
            stop_listeners()
            return False  # Stop the listener
        elif key == keyboard.KeyCode.from_char('d'):
            recording_switch()
        elif key == keyboard.KeyCode.from_char('y'):
            replaying = not replaying
            print(f"{'Started' if replaying else 'Stopped'} replay...")
            if replaying:
                recording = False  # Stop recording if replaying starts
                # Also stop mouse listener if it was running
                if mouse_listener and mouse_listener.running:
                    mouse_listener.stop()
                    print("Mouse listener stopped for replay")
                replay_thread = threading.Thread(target=replay_clicks)
                replay_thread.daemon = True
                replay_thread.start()
        elif key == keyboard.KeyCode.from_char('c'):
            clear_clicks()
    except AttributeError:
        # Handle special keys that don't have char representation
        pass
    

def recording_switch():
    """
    Starts recording mouse clicks.
    """
    global recording, replaying, mouse_listener
    recording = not recording

    if recording:
        replaying = False  # Stop replay if recording is started
        # Start mouse listener when recording starts
        if mouse_listener is None or not mouse_listener.running:
            mouse_listener = mouse.Listener(on_click=on_click)
            mouse_listener.daemon = True
            mouse_listener.start()
            print("Mouse listener started for recording")
    else:
        # Stop mouse listener when recording stops
        if mouse_listener and mouse_listener.running:
            mouse_listener.stop()
            print("Mouse listener stopped")
    
    print(f"Recording {'started' if recording else 'stopped'}")

def start_listeners():
    """
    Starts only the keyboard listener.
    """
    global key_listener
    
    if key_listener is None or not key_listener.running:
        key_listener = keyboard.Listener(on_press=on_press)
        key_listener.daemon = True
        key_listener.start()
        print("Keyboard listener started")

def start_keyboard_listener():
    """
    Starts only the keyboard listener (for button control).
    """
    start_listeners()

def stop_keyboard_listener():
    """
    Stops only the keyboard listener.
    """
    global key_listener
    
    if key_listener and key_listener.running:
        key_listener.stop()
        print("Keyboard listener stopped")

def stop_listeners():
    """
    Stops both keyboard and mouse listeners.
    """
    global key_listener, mouse_listener, replaying
    
    replaying = False
    
    if key_listener and key_listener.running:
        key_listener.stop()
        print("Keyboard listener stopped")
    
    if mouse_listener and mouse_listener.running:
        mouse_listener.stop()
        print("Mouse listener stopped")

def clear_clicks():
    """
    Clears the recorded click positions.
    """
    global click_positions
    click_positions = []
    print("Click positions cleared.")

def replay_clicks():
    """
    Replays the recorded clicks at the stored positions with individual delays and offsets.
    """
    global click_positions, replaying

    if not click_positions:
        print("No clicks recorded to replay")
        return

    cycle_count = 0
    while replaying:
        cycle_count += 1
        print(f"Starting replay cycle #{cycle_count}")

        for i, click_obj in enumerate(click_positions):
            if not replaying:  # Check if we should stop
                break
            # Calculate position with offset for this cycle
            current_x = click_obj.x + (click_obj.offset_x * (cycle_count - 1))
            current_y = click_obj.y + (click_obj.offset_y * (cycle_count - 1))

            # If this item is a scroll action, perform scroll instead of click
            if getattr(click_obj, 'is_scroll', False):
                try:
                    # Ensure mouse is at the intended coordinates before scrolling.
                    # Some platforms/drivers ignore x/y in scroll, so move first then scroll.
                    pyautogui.moveTo(current_x, current_y)
                    # tiny pause to ensure OS updates pointer location
                    time.sleep(0.02)
                    pyautogui.scroll(int(click_obj.scroll_amount))
                    print(f"Scrolled {click_obj.scroll_amount} at: ({current_x}, {current_y})")
                except Exception as e:
                    print(f"Scroll failed: {e}")
            else:
                # Perform the click
                if click_obj.is_double_click:
                    pyautogui.doubleClick(current_x, current_y)
                    print(f"Double-clicked at: ({current_x}, {current_y})")
                else:
                    pyautogui.click(current_x, current_y)
                    print(f"Clicked at: ({current_x}, {current_y})")

            # Wait for the specified delay after this click/scroll
            if getattr(click_obj, 'delay', 0) > 0:
                time.sleep(click_obj.delay)

        # Optional: small delay between cycles
        if replaying and cycle_count < 100:  # Prevent infinite loops
            time.sleep(0.1)  # Small pause between cycles

    print("Replay finished")

# not used yet
def double_click_n_copy():
    """
    Double-clicks at the current mouse position and copies the selected text.
    """
    global replaying
    if not replaying:
        print("Not in replay mode, cannot double-click and copy")
        return
    
    current_pos = pyautogui.position()
    pyautogui.doubleClick(current_pos)
    time.sleep(0.1)  # Small delay to ensure double-click is registered
    pyautogui.hotkey('ctrl', 'c')  # Copy the selected text
    print(f"Double-clicked and copied text at: {current_pos}")

if __name__ == "__main__":
    # Don't start any listeners by default when running directly
    print("ClickNCommand module loaded. Use GUI to control listeners.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user")
        stop_listeners()

# implement it do other commands after a click + timed clicks
# am I writing a macro tho?
# need listview for clicks that has been recorded and gui to modify them
