import threading
import queue
import logging

logging.basicConfig(filename='task_loop.log', level=logging.INFO)

class MainLoopArchitecture:
    def __init__(self):
        self.command_queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.error_queue = queue.Queue()  # Added for error handling
        self.main_loop_thread = threading.Thread(target=self.main_loop)
        self.user_input_thread = threading.Thread(target=self.listen_for_user_input)
        self.main_loop_thread.daemon = True
        self.user_input_thread.daemon = True

    def start(self):
        try:
            self.main_loop_thread.start()
            self.user_input_thread.start()
            logging.info("Threads started.")
        except Exception as e:
            self.error_queue.put(f"Error starting threads: {e}")
            logging.error(f"Error starting threads: {e}")

    def stop(self):
        try:
            self.main_loop_thread.join()
            self.user_input_thread.join()
            logging.info("Threads stopped.")
        except Exception as e:
            self.error_queue.put(f"Error stopping threads: {e}")
            logging.error(f"Error stopping threads: {e}")

    def main_loop(self):
        try:
            while True:
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    self.handle_command(command)
        except Exception as e:
            self.error_queue.put(f"Error in main loop: {e}")
            logging.error(f"Error in main loop: {e}")

    def listen_for_user_input(self):
        try:
            while True:
                user_input = input("Enter command: ")
                if user_input:
                    self.command_queue.put(user_input)
        except Exception as e:
            self.error_queue.put(f"Error listening for user input: {e}")
            logging.error(f"Error listening for user input: {e}")

    def handle_command(self, command):
        try:
            if command == "stop":
                self.stop()
            elif command == "pause":
                self.pause()
            elif command == "help":
                self.show_help()
            elif command.startswith("inject prompt"):
                _, prompt = command.split(" ", 1)
                self.inject_prompt(prompt)
            self.status_queue.put(f"Handled command: {command}")
            logging.info(f"Handled command: {command}")
        except Exception as e:
            self.error_queue.put(f"Error handling command: {command}, Error: {e}")
            logging.error(f"Error handling command: {command}, Error: {e}")

    def pause(self):
        try:
            self.is_paused = not self.is_paused
            print("Pause toggled.")
        except Exception as e:
            self.error_queue.put(f"Error toggling pause: {e}")
            logging.error(f"Error toggling pause: {e}")

    def show_help(self):
        print("Showing help...")
        logging.info("Showing help...")

    def inject_prompt(self, prompt):
        print(f"Injecting prompt: {prompt}")
        logging.info(f"Injecting prompt: {prompt}")
