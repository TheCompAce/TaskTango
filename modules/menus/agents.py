import json
import os

def add_agent():
    # Gather information for a new agent
    agent_info = {}
    agent_info["agent_name"] = input("Enter the name of the agent: ")
    agent_info["description"] = input("Enter the description of the agent: ")
    agent_info["type"] = input("Enter the overall type (e.g., llm, human, custom): ")
    agent_info["model"] = input("Enter the model name (e.g., OpenAI): ")
    agent_info["system_prompt"] = input("Enter the system prompt for the agent: ")
    agent_info["capabilities"] = input("Enter the capabilities (comma-separated): ").split(",")
    
    # Save the agent information to a JSON file
    agent_file_path = os.path.join("agents", "agent_configs", f"{agent_info['agent_name']}.json")
    with open(agent_file_path, "w") as f:
        json.dump(agent_info, f, indent=4)

def edit_agent():
    # List available agents for editing
    agent_files = os.listdir(os.path.join("agents", "agent_configs"))
    print("Available agents for editing:")
    for idx, agent_file in enumerate(agent_files):
        print(f"{idx+1}. {agent_file[:-5]}")
    choice = input("Select an agent to edit (by number) or type 'back' to go back: ")
    if choice.lower() == "back":
        return
    selected_agent_file = agent_files[int(choice) - 1]
    
    # Load the selected agent's configuration
    agent_file_path = os.path.join("agents", "agent_configs", selected_agent_file)
    with open(agent_file_path, "r") as f:
        agent_info = json.load(f)
        
    # Edit the agent's configuration
    for key in agent_info.keys():
        new_value = input(f"Current {key}: {agent_info[key]} -- Enter new value (or press Enter to keep current): ")
        if new_value:
            agent_info[key] = new_value
            
    # Save the edited agent configuration
    with open(agent_file_path, "w") as f:
        json.dump(agent_info, f, indent=4)

def delete_agent():
    # List available agents for deletion
    agent_files = os.listdir(os.path.join("agents", "agent_configs"))
    print("Available agents for deletion:")
    for idx, agent_file in enumerate(agent_files):
        print(f"{idx+1}. {agent_file[:-5]}")
    choice = input("Select an agent to delete (by number) or type 'back' to go back: ")
    if choice.lower() == "back":
        return
    selected_agent_file = agent_files[int(choice) - 1]
    
    # Confirm before deletion
    confirm = input(f"Are you sure you want to delete {selected_agent_file[:-5]}? (yes/no): ")
    if confirm.lower() == "yes":
        os.remove(os.path.join("agents", "agent_configs", selected_agent_file))
        print("Agent deleted successfully.")
    else:
        print("Deletion cancelled.")

def agent_menu():
    while True:
        print("===== Agent Menu =====")
        print("1. Add Agent")
        print("2. Edit Agent")
        print("3. Delete Agent")
        print("4. Back")
        choice = input("Please choose an option: ")
        
        if choice == "1":
            add_agent()
        elif choice == "2":
            edit_agent()
        elif choice == "3":
            delete_agent()
        elif choice == "4":
            return  # Go back to the previous menu
        else:
            print("Invalid choice. Please try again.")
