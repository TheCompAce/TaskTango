import json
import logging
import os
import queue
from modules.mainLoopArchitecture import MainLoopArchitecture
from modules.utils.get_id import generate_uuid
from modules.llm import LLM, ModelTypes
from modules.vectorDatabase import VectorDatabase

logging.basicConfig(filename='task_loop.log', level=logging.INFO)

class TaskManager(MainLoopArchitecture):
    def __init__(self, config_file, prompt):
        super().__init__()
        # Initialize variables and configurations
        self.config = self.load_config(config_file)
        self.task_id = generate_uuid()  # Using the utility function to generate a unique ID
        self.tasks = None
        self.group_order = []
        self.prompt = prompt
        self.llm_queue = queue.Queue()
        self.llm_result_queue = queue.Queue()
        self.llm_handler = LLM(ModelTypes(self.config["model"]))  # Initialize the LLM handler
        self.llm_simple_handler = LLM(ModelTypes.Zephyr7bAlpha)

        self.vector_db = VectorDatabase(path='server\data', name='long_term')
        
    def execute(self):
        logging.info(f"execute")
        self.start()  # Start the main loop thread and user input thread
        logging.info(f"execute - start")
        # Read config properties
        task_config = self.config  # Assuming self.config contains the task settings

        task_data_prompt = "Return the data as a JSON object."
        if os.path.exists("system/prompts/task_data.txt"):
            with open("system/prompts/task_data.txt", 'r') as f:
                task_data_prompt = f.read()
        
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
            groups=[]
            for group in task_config["groups"]:
                groups.append(self.get_group_config(group))

            group_order_prompt = "Determine group order, and return a single JSON array of group names."
            if os.path.exists("system/prompts/group_order.txt"):
                with open("system/prompts/group_order.txt", 'r') as f:
                    group_order_prompt = f.read()

            group_order_prompt = group_order_prompt + "\nOrder group for \"" + self.prompt + "\"."

            groups_json = json.dumps(groups)

            group_order_response = self.llm_simple_handler.ask(group_order_prompt, groups_json)

            logging.info(f"group_order_response = " + group_order_response)

            try:
                group_order = json.loads(group_order_response)
            except:
                logging.info(f"Failed to get groups - {group_order_response}")

        self.group_order = group_order
    
        prompts_json_string = json.dumps(prompts_json_object)

        system_prompt = self.config["systemPrompt"]  # Extract the system prompt from the config
        if os.path.isfile(system_prompt):
            with open(system_prompt, 'r') as f:
                system_prompt = f.read()

        system_prompt = system_prompt + "\n" + task_data_prompt

        system_prompt_full = prompts_json_string + "\n" + system_prompt

        logging.info(f"system_prompt_full: {system_prompt_full}")
        
        self.llm_queue.put([system_prompt_full, self.prompt, self.config["model"]] ) 
        

    # Overriding main_loop to add task-specific logic
    def main_loop(self):
        try:
            while True:
                if not self.llm_queue.empty():
                    llm_data = self.llm_queue.get()
                    logging.info(f"system: {llm_data[0]}")
                    logging.info(f"user: {llm_data[1]}")
                    logging.info(f"model: {llm_data[2]}")
                    # Ask the LLM for a response
                    self.llm_handler.ClearModel(llm_data[2])

                    response = self.llm_handler.ask(llm_data[0], llm_data[1])

                    logging.info(f"response: {response}")
                    self.status_queue.put(response)  # Put the response into the status queue

                    self.llm_result_queue.put([llm_data[0], llm_data[1], llm_data[2], response])


                if not self.llm_result_queue.empty():
                    llm_result = self.llm_result_queue.get()
                    self.handle_result(llm_result[0], llm_result[1], llm_result[2], llm_result[3])

        except Exception as e:
            self.error_queue.put(f"Error in TaskManager's main_loop: {e}")
            logging.error(f"Error in TaskManager's main_loop: {e}")
        finally:
            super().main_loop()

    def handle_result(self, system_prompt, user_prompt, model, response_text):
        try:
            logging.info("response_text = " + response_text)
            task_data = json.loads(response_text)

            task_id = task_data.get("taskid", None)
            logging.info("task_id = " + task_id)

            if task_id is not None:
                if task_id == "task_data":
                    logging.info("task_data = " + json.dumps(task_data))
                    tasks = task_data.get("tasks", None)
                    self.tasks = tasks

                    logging.info("self.tasks = " + json.dumps(self.tasks))
                    
                    while self.is_paused:
                        pass

        except  Exception as e:
            self.error_queue.put(f"Error in TaskManager's handle_result: {e}, {response_text}")
            logging.error(f"Error in TaskManager's handle_result: {e}, {response_text}")
            self.llm_queue.put([system_prompt, user_prompt, model])

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
        # Assume group configurations are stored in a 'groups_config' directory
        config_dir_path = 'groups/group_configs'
        for config_file_name in os.listdir(config_dir_path):
            config_file_path = os.path.join(config_dir_path, config_file_name)
            if os.path.isfile(config_file_path):
                with open(config_file_path, 'r') as config_file:
                    group_config = json.load(config_file)
                if "groupName" in group_config and group_config["groupName"] == group_name:
                    return group_config
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
