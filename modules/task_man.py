import json
from modules.mainLoopArchitecture import MainLoopArchitecture
from modules.utils.get_id import generate_uuid
from modules.llm import LLM

class TaskManager(MainLoopArchitecture):
    def __init__(self, config_file, prompt):
        super().__init__()
        # Initialize variables and configurations
        self.config = self.load_config(config_file)
        self.task_id = generate_uuid()  # Using the utility function to generate a unique ID
        self.prompt = prompt
        self.llm_handler = LLM(self.config["model"])  # Initialize the LLM handler
        
    def execute(self):
        self.start()  # Start the main loop thread and user input thread
        system_prompt = self.config["systemPrompt"]  # Extract the system prompt from the config
        if os.path.isfile(system_prompt):
            with open(system_prompt, 'r') as f:
                system_prompt = f.read()
                
        # Ask the LLM for a response
        response = self.llm_handler.ask(system_prompt, self.prompt)
        self.status_queue.put(response)  # Put the response into the status queue
        self.stop()  # Stop the main loop thread and user input thread

    def load_config(self, config_file):
        """
        Load the configuration from a JSON file.
        """
        with open(config_file, 'r') as f:
            return json.load(f)

    def handle_command(self, command):
        """
        Override the handle_command method to include task-specific commands
        """
        super().handle_command(command)
        # Add more task-specific commands and functionalities as required
