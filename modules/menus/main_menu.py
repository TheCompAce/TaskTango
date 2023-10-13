from modules.menus.agents import agent_menu
from modules.menus.groups import groups_menu
from modules.menus.tasks import task_menu

def setup_agent():
    agent_menu()

def setup_group():
    groups_menu()

def setup_task():
    task_menu()

def start_task(task_id):
    print("Starting task with ID:", task_id)

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
            start_task("Task ID Here")
        elif choice == '5':
            exit_system()
            break
        else:
            print("Invalid choice. Please try again.")
