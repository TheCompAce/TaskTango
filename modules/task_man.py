import json
import os
from modules.mainLoopArchitecture import MainLoopArchitecture
from modules.utils.get_id import generate_uuid
from modules.llm import LLM, ModelTypes

class TaskManager(MainLoopArchitecture):
    def __init__(self, config_file, prompt):
        super().__init__()
        # Initialize variables and configurations
        self.config = self.load_config(config_file)
        self.task_id = generate_uuid()  # Using the utility function to generate a unique ID
        self.prompt = prompt
        self.llm_handler = LLM(self.config["model"])  # Initialize the LLM handler
        self.llm_simple_handler = LLM(ModelTypes.StableBeluga7B)
        
    def execute(self):
        self.start()  # Start the main loop thread and user input thread

        # Read config properties
        task_config = self.config  # Assuming self.config contains the task settings
        
        # Create the prompts JSON object
        prompts_json_object = {
            "task": {
                "id": task_config["taskName"],
                "variables": task_config["variables"],
                "completionIndicators": task_config["completionIndicators"]
            }
        }

        groups_list = task_config["groups"]

        if len(task_config["groups"]) > 1:
            group_order_prompt = "Determine group order"
            if os.path.exists("system/prompts/group_order.txt"):
                with open(group_order_prompt, 'r') as f:
                    group_order_prompt = f.read()

            group_order_prompt = group_order_prompt + "\nUser Task: \"" + self.prompt + "\""

            group_order_response = self.llm_simple_handler.ask(group_order_prompt, task_config["groups"])

        prompts_json_string = json.dumps(prompts_json_object)

        system_prompt = self.config["systemPrompt"]  # Extract the system prompt from the config
        if os.path.isfile(system_prompt):
            with open(system_prompt, 'r') as f:
                system_prompt = f.read()

        system_prompt_full = system_prompt

        system_prompt_full = system_prompt_full + "\n" + prompts_json_string
                
        # Ask the LLM for a response
        response = self.llm_handler.ask(system_prompt_full, self.prompt)
        self.status_queue.put(response)  # Put the response into the status queue
        self.pause()  # Stop the main loop thread and user input thread

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
