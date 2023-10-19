import json
import os
from modules.menus.agents import agent_menu
from modules.menus.groups import groups_menu
from modules.menus.tasks import task_menu
from modules.task_man import TaskManager

def setup_agent():
    agent_menu()

def setup_group():
    groups_menu()

def setup_task():
    task_menu()

def start_task():
    task_configs_path = "tasks/task_configs"  # Update this to your actual path
    task_files = os.listdir(task_configs_path)
    
    while True:
        print("===== Task List =====")
        for idx, task_file in enumerate(task_files):
            with open(os.path.join(task_configs_path, task_file), 'r') as f:
                task_config = json.load(f)
            print(f"{idx + 1}. {task_config.get('taskName', 'Unnamed Task')}")
        print(f"{len(task_files) + 1}. Back")
        
        choice = input("Select a task or go back: ")
        if choice.isdigit() and 1 <= int(choice) <= len(task_files):
            selected_task_file = task_files[int(choice) - 1]
            with open(os.path.join(task_configs_path, selected_task_file), 'r') as f:
                selected_task_config = json.load(f)
            print(f"Starting task: {selected_task_config.get('taskName', 'Unnamed Task')}")

            start_prompt = input("What do you want this task to accomplish?")

            # Check if the input is a path to a file
            if os.path.isfile(start_prompt):
                with open(start_prompt, 'r') as f:
                    start_prompt = f.read()


            # Initialize TaskManager
            task_manager = TaskManager(config_file=os.path.join(task_configs_path, task_file), prompt=start_prompt)
            
            # Start the task
            task_manager.execute()
            
            # Wait for the task to complete
            task_manager.join()
            
            break
        elif choice == str(len(task_files) + 1):
            print("Going back to main menu.")
            break
        else:
            print("Invalid choice. Please try again.")

def exit_system():
    print("Exiting system gracefully")

def show_menu():
    while True:
        print("===== Main Menu =====")
        print("1. Setup Agents")
        print("2. Setup Groups")
        print("3. Setup Tasks")
        print("4. Start Task")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            setup_agent()
        elif choice == '2':
            setup_group()
        elif choice == '3':
            setup_task()
        elif choice == '4':
            start_task()
        elif choice == '5':
            exit_system()
            break
        else:
            print("Invalid choice. Please try again.")
