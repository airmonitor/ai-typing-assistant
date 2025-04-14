"""
Microphone Toggle Script for macOS
---------------------------------
This script listens for F6 key presses and toggles the microphone on/off.
Run this script in the background to enable the F6 microphone toggle functionality.
"""

import subprocess
import time

from pynput import keyboard


def get_mic_volume():
    """Get the current microphone input volume (0-100)"""
    cmd = "osascript -e 'input volume of (get volume settings)'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
    try:
        return int(result.stdout.strip())
    except ValueError:
        # In case of an error, return 0
        return 0


def set_mic_volume(volume):
    """Set the microphone input volume (0-100)"""
    cmd = f"osascript -e 'set volume input volume {volume}'"
    subprocess.run(cmd, shell=True, check=False)


def toggle_microphone():
    """Toggle the microphone between muted (0) and unmuted (100)"""
    current_volume = get_mic_volume()

    # If volume is 0, set to 100, otherwise set to 0
    new_volume = 100 if current_volume == 0 else 0
    set_mic_volume(new_volume)

    # Print status to console
    state = "UNMUTED" if new_volume == 100 else "MUTED"
    print(f"[{time.strftime('%H:%M:%S')}] Microphone is now {state}")

    # Show a notification about the new microphone state
    subprocess.run(
        ["osascript", "-e", f'display notification "Microphone is now {state}" with title "Mic Toggle"'], check=False
    )


def on_press(key):
    """Handle key press events"""
    if key == keyboard.Key.f6:
        print(f"[{time.strftime('%H:%M:%S')}] F6 pressed - toggling microphone")
        toggle_microphone()


def main():
    """Main function to set up the keyboard listener and run the script"""
    # Print the script header
    print("\n" + "=" * 60)
    print("MICROPHONE TOGGLE SCRIPT".center(60))
    print("=" * 60)
    print("This script allows you to toggle your microphone on/off using F6.")
    print("Current microphone status:", "UNMUTED" if get_mic_volume() > 0 else "MUTED")
    print("\nPress F6 to toggle microphone")
    print("Press Ctrl+C to exit")
    print("-" * 60)

    # Set up the keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C to exit gracefully
        listener.stop()
        print("\n" + "-" * 60)
        print("Microphone toggle script stopped.")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
