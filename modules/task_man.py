import json
import os
from modules.mainLoopArchitecture import MainLoopArchitecture
from modules.utils.get_id import generate_uuid
from modules.llm import LLM, ModelTypes
from modules.vectorDatabase import VectorDatabase

class TaskManager(MainLoopArchitecture):
    def __init__(self, config_file, prompt):
        super().__init__()
        # Initialize variables and configurations
        self.config = self.load_config(config_file)
        self.task_id = generate_uuid()  # Using the utility function to generate a unique ID
        self.prompt = prompt
        self.llm_handler = LLM(self.config["model"])  # Initialize the LLM handler
        self.llm_simple_handler = LLM(ModelTypes.StableBeluga7B)

        self.vector_db = VectorDatabase(path='server\data', name='long_term')
        
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

        group_order = task_config["groups"]

        if len(task_config["groups"]) > 1:
            group_order_prompt = "Determine group order"
            if os.path.exists("system/prompts/group_order.txt"):
                with open(group_order_prompt, 'r') as f:
                    group_order_prompt = f.read()

            group_order_prompt = group_order_prompt + "\nUser Task: \"" + self.prompt + "\""

            group_order_response = self.llm_simple_handler.ask(group_order_prompt, task_config["groups"])

            group_order = json.loads(group_order_response)
        
        task_prompts_json_object=prompts_json_object
        for group_name in group_order:
            group_config = self.get_group_config(group_name)

            prompts_json_object = task_prompts_json_object

            prompts_json_object["group"]= {
                "name": group_name,
                "variables": group_config["variables"],
                "completionIndicators": group_config["completionIndicators"]
            }

            prompts_json_string = json.dumps(prompts_json_object)

            system_prompt = self.config["systemPrompt"]  # Extract the system prompt from the config
            if os.path.isfile(system_prompt):
                with open(system_prompt, 'r') as f:
                    system_prompt = f.read()

            system_prompt_full = system_prompt + "\n" + prompts_json_string
                    
            # Ask the LLM for a response
            response = self.llm_handler.ask(system_prompt_full, self.prompt)
            self.status_queue.put(response)  # Put the response into the status queue

            self.pause()  # Stop the main loop thread and user input thread

        self.stop()  # Stop the main loop thread and user input thread

    def create_response(self, response_text):
        return self.vector_db.create_response(response_text)

    def search_response(self, search_text):
        return self.vector_db.search_response(search_text)

    def update_response(self, response_id, new_response_text):
        return self.vector_db.update_response(response_id, new_response_text)

    def delete_response(self, response_id):
        return self.vector_db.delete_response(response_id)

    def train_untrained_responses(self):
        return self.vector_db.train_untrained_responses()

    def search_similar_conversations(self, text, top_n=5):
        return self.vector_db.search_similar_conversations(text, top_n=top_n)

    def get_group_config(self, group_name):
        # Assume group configurations are stored in json files named after the group in a 'groups_config' directory
        config_file_path = f'groups/groups_config/{group_name}.json'
        if os.path.isfile(config_file_path):
            with open(config_file_path, 'r') as config_file:
                group_config = json.load(config_file)
            return group_config
        else:
            raise FileNotFoundError(f'Configuration file for group {group_name} not found.')

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
