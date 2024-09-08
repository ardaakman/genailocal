import subprocess
import time
import requests
import os
import io
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
        self.is_typing_programmatically = False

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
        screenshot = pyautogui.screenshot()
        screenshot_buffer = io.BytesIO()
        screenshot.save(screenshot_buffer, format='PNG')
        screenshot_buffer.seek(0)
        
        current_app = self.get_active_app()

        # Send api request to endpoint. 
        for _ in range(len(self.recent_keystrokes)):
            self.keyboard_controller.press(Key.backspace)
            self.keyboard_controller.release(Key.backspace)
        # Send api request to the endpoint.
        # Send the screenshot, current_app, keyboard_input_so_far
        try:
            resp = requests.post(
                "http://localhost:8080/inference",
                json={"prompt": self.recent_keystrokes, "source": current_app}
            )
            resp.raise_for_status()  # Raise an exception for bad status codes

            self.recent_keystrokes = ""
            # Output the response with keystrokes.
            result = resp.json().get('result', '')
            self.is_typing_programmatically = True
            for index, char in enumerate(result):
                logging.debug(f"Typing character {index}: {repr(char)}")
                try:
                    if char == '\n':
                        self.keyboard_controller.press(Key.enter)
                        self.keyboard_controller.release(Key.enter)
                    elif char.isprintable():
                        self.keyboard_controller.press(char)
                        self.keyboard_controller.release(char)
                    else:
                        logging.warning(f"Skipping non-printable character: {repr(char)}")
                    time.sleep(0.02)  # Adjust this delay as needed
                except Exception as e:
                    logging.exception(f"Error typing character {index} ({repr(char)}): {e}")
                    # Optionally break here if you want to stop on first error
                    self.is_typing_programmatically = False
            self.is_typing_programmatically = False
            logging.info("Typing process completed")

        except requests.exceptions.RequestException as e:
            print(f"Error sending inference request: {e}")
        

    def on_press(self, key):
        self.last_keystroke_time = time.time()
        if self.is_typing_programmatically:
            return
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
            screenshot_path = os.path.join(os.getcwd(), screenshot_name)
            screenshot.save(screenshot_path)
            active_app = self.get_active_app()
            time.sleep(5)

            try:
                # Send the screenshot to the backend
                with open(screenshot_path, 'rb') as file:
                    requests.post("http://localhost:8080/process-image", files={"file": file}, data={"source": active_app})
                
                # Delete the file
                os.remove(screenshot_path)
                logging.info(f"Screenshot {screenshot_name} deleted.")
            except Exception as e:
                logging.error(f"Error processing or deleting screenshot {screenshot_name}: {e}")


    def run(self):
        screen_thread = threading.Thread(target=self.capture_screen)
        screen_thread.daemon = True
        screen_thread.start()

        self.run_listener()

if __name__ == "__main__":
    monitor = KeystrokeMonitor()
    monitor.run()
