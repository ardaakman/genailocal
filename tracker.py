import subprocess
import time
import requests
import os
import logging
from pynput import keyboard
from pynput.keyboard import Key, Controller
import pyautogui
import threading
from AppKit import NSWorkspace

class KeystrokeMonitor:
    def __init__(self):
        self.TIMEOUT = 10
        # Set up logging
        logging.basicConfig(filename='keystroke_monitor.log', level=logging.INFO,
                            format='%(asctime)s - %(message)s')

        # Initialize the keyboard controller
        self.keyboard_controller = Controller()

        # Variable to store the recent keystrokes
        self.recent_keystrokes = ""

        self.commands = {
            "/hello_world": lambda: self.type_string("Hello, World!"),
            "#//" : self.handle_fill_command,
        }

        # Random messages
        self.chrome_messages = [
            "Chrome is ready to surf the web!",
            "Time to explore the internet with Chrome!",
            "Chrome launched. What will you discover today?",
            "Your gateway to the web is now open.",
            "Chrome at your service. Happy browsing!"
        ]

        self.alternative_browsers = [
            "How about trying Safari?",
            "Firefox might be a good alternative.",
            "Opera is an interesting browser option.",
            "Have you considered Brave browser?",
            "Microsoft Edge could be worth a look."
        ]

    def get_active_app(self):
        active_app = NSWorkspace.sharedWorkspace().activeApplication()
        app_name = active_app['NSApplicationName']
        window_title = active_app['NSApplicationPath'].split('/')[-1].split('.')[0]
        return f"{app_name} ({window_title})"

    def type_string(self, string):
        for char in string:
            self.keyboard_controller.press(char)
            self.keyboard_controller.release(char)
            time.sleep(0.05)  # Small delay, can be tuned accordingly. Make it feel organic.

    def is_chrome_installed(self):
        try:
            return subprocess.call(["osascript", "-e", 'tell application "System Events" to (name of processes) contains "Google Chrome"']) == 0
        except Exception as e:
            logging.error(f"Error checking Chrome installation: {e}")
            return False

    def open_chrome(self):
        try:
            subprocess.Popen(["open", "-a", "Google Chrome"])
        except Exception as e:
            logging.error(f"Error opening Chrome: {e}")

    def handle_fill_command(self):
        self.is_capturing = True
        self.last_keystroke_time = time.time()
        self.recent_keystrokes = ""
        
        # Start a timer to check for input completion
        threading.Thread(target=self.check_input_completion, daemon=True).start()

    def check_input_completion(self):
        while self.is_capturing:
            time.sleep(0.1)
            if time.time() - self.last_keystroke_time > self.TIMEOUT or not(self.is_capturing):
                # Auto-timeout if its taking too long to input tab.
                self.process_captured_input()

    def process_captured_input(self):
        # Process the captured input and call the API
        current_app = self.get_active_app()
        # Take a screenshot as well, with current_app, keyboard_input_so_far, screenshot
        screenshot = pyautogui.screenshot()
        # Send api request to endpoint. 
        for _ in range(len(self.recent_keystrokes)):
            self.keyboard_controller.press(Key.backspace)
            self.keyboard_controller.release(Key.backspace)
        print(current_app, self.recent_keystrokes)
        # Send api request to the endpoint.
        # Send the screenshot, current_app, keyboard_input_so_far
        resp = requests.post("http://localhost:8080/inference", files={"file": screenshot}, data={"prompt": self.recent_keystrokes, "source": current_app})
        self.recent_keystrokes = ""
        # Output the response with keystrokes.
        for char in resp.json()['result']:
            self.keyboard_controller.press(char)
            self.keyboard_controller.release(char)
            time.sleep(0.05)
        

    def on_press(self, key):
        self.last_keystroke_time = time.time()
        try:
            if isinstance(key, keyboard.KeyCode):
                self.recent_keystrokes += key.char
            elif key == Key.space:
                self.recent_keystrokes += " "
            elif key == Key.enter:
                self.recent_keystrokes += "\n"
            elif key == Key.ctrl:
                self.is_capturing = False

        except AttributeError:
            pass
        
        # Check for any command triggers
        for cmd, func in self.commands.items():
            if self.recent_keystrokes.endswith(cmd):
                # Clear the typed command
                for _ in range(len(cmd)):
                    self.keyboard_controller.press(Key.backspace)
                    self.keyboard_controller.release(Key.backspace)
                
                # Execute the command
                func()
                
                # Log the execution with the active app info
                logging.info(f"Executed command: {cmd}")
                
                self.recent_keystrokes = ""
                return
        
        self.recent_keystrokes = self.recent_keystrokes[-50:]

    def run_listener(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            logging.info("Keystroke monitor started")
            try:
                listener.join()
            except Exception as e:
                logging.error(f"Error in listener: {e}")
                time.sleep(1) 
                self.run_listener()

    def capture_screen(self):
        while True:
            screenshot = pyautogui.screenshot()
            screenshot_name = f"screenshot_{int(time.time())}.png"
            screenshot.save(screenshot_name)
            active_app = self.get_active_app()
            time.sleep(5)
            # Send it to backend after figuring out the backend stuff. Then delete the file.
            # Delete the named file from namespace.
            try:
                # Send the screenshot to the backend.
                requests.post("http://localhost:8080/process-image", files={"file": screenshot}, data={"source": active_app})
                os.remove(screenshot_name)
                logging.info(f"Screenshot {screenshot_name} deleted.")
            except Exception as e:
                logging.error(f"Error deleting screenshot {screenshot_name}: {e}")


    def run(self):
        screen_thread = threading.Thread(target=self.capture_screen)
        screen_thread.daemon = True
        screen_thread.start()

        self.run_listener()

if __name__ == "__main__":
    monitor = KeystrokeMonitor()
    monitor.run()
