import signal
import threading
import queue
import logging

logging.basicConfig(filename='base_loop.log', level=logging.INFO)

class MainLoopArchitecture:
    def __init__(self):
        self.command_queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self.is_paused = False
        
        self.main_loop_thread = threading.Thread(target=self.main_loop)
        self.user_input_thread = threading.Thread(target=self.listen_for_user_input)
        self.main_loop_thread.daemon = True
        self.user_input_thread.daemon = True

        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal, frame):
        self.stop()


    def start(self):
        try:
            self.main_loop_thread.start()
            self.user_input_thread.start()
            logging.info("Threads started.")
        except Exception as e:
            self.error_queue.put(f"Error starting threads: {e}")

    def stop(self):
        try:
            self.stop_event.set()
            self.main_loop_thread.join()
            self.user_input_thread.join()
            logging.info("Threads stopped.")
        except Exception as e:
            self.error_queue.put(f"Error stopping threads: {e}")

    def main_loop(self):
        try:
            while True:
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    self.handle_command(command)
                if not self.error_queue.empty():
                    error = self.error_queue.get()
                    self.status_queue.put("Error : " + error)
                    logging.error(f"Error : {error}")
        except Exception as e:
            self.error_queue.put(f"Error in main loop: {e}")
            logging.error(f"Error in main loop: {e}")

    def listen_for_user_input(self):
        try:
            while not self.stop_event.is_set():
                user_input = input("Enter command: ")
                if user_input:
                    self.command_queue.put(user_input)
        except Exception as e:
            self.error_queue.put(f"Error listening for user input: {e}")

    def handle_command(self, command):
        try:
            print("Send Command : " + command)
            if command == "stop":
                self.stop()
            elif command == "pause":
                self.pause()
            elif command == "help":
                self.show_help()
            else: #if command.startswith("inject prompt"):
                _, prompt = command.split(" ", 1)
                self.inject_prompt(prompt)

            self.status_queue.put(f"Handled command: {command}")
            logging.info(f"Handled command: {command}")
        except Exception as e:
            self.error_queue.put(f"Error handling command: {command}, Error: {e}")

    def pause(self):
        try:
            self.is_paused = not self.is_paused
            self.status_queue.put("Pause toggled.")
        except Exception as e:
            self.error_queue.put(f"Error toggling pause: {e}")

    def show_help(self):
        self.status_queue.put("Showing help...")

    def inject_prompt(self, prompt):
        self.status_queue.put(f"Injecting prompt: {prompt}")
        logging.info(f"Injecting prompt: {prompt}")

    def join(self):
        try:
            self.main_loop_thread.join()
            self.user_input_thread.join()
            logging.info("Threads joined.")
        except Exception as e:
            self.error_queue.put(f"Error joining threads: {e}")
