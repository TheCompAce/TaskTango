import json
import os

def add_group():
    # Gather information for a new group
    group_info = {}
    group_info["groupName"] = input("Enter the groupName: ")
    group_info["systemPrompt"] = input("Enter the systemPrompt: ")
    group_info["agents"] = input("Enter the agents: ")
    group_info["completionIndicators"] = input("Enter the completionIndicators: ")
    group_info["variables"] = input("Enter the variables: ")
    group_info["dynamicAgentAllocation"] = input("Enter the dynamicAgentAllocation: ")
    group_info["longTerm"] = input("Enter the longTerm: ")
    group_info["interGroupCommunication"] = input("Enter the interGroupCommunication: ")
    group_info["allowAgentCloning"] = input("Enter the allowAgentCloning: ")
    group_info["notification"] = input("Enter the notification: ")

    # Save the group information to a JSON file
    with open(f"groups/{group_info['groupName']}.json", 'w') as f:
        json.dump(group_info, f, indent=4)

def edit_group():
    try:
        available_groups = os.listdir("groups")
        print("Available Groups:")
        for group in available_groups:
            print(f" - {group.replace('.json', '')}")
        print(" - Back")
    except FileNotFoundError:
        print("No groups found.")
        return

    group_name = input("Enter the name of the group to edit or 'Back' to return: ")
    if group_name.lower() == 'back':
        return
    
    try:
        with open(f"groups/{group_name}.json", 'r') as f:
            group_info = json.load(f)
        print(f"Editing group: {group_name}")
        for key in group_info.keys():
            new_value = input(f"Current {key}: {group_info[key]}\\nEnter new value or press Enter to keep: ")
            if new_value:
                group_info[key] = new_value
        # Save the updated group information
        with open(f"groups/{group_info['groupName']}.json", 'w') as f:
            json.dump(group_info, f, indent=4)
        print(f"Group {group_name} edited successfully.")
    except FileNotFoundError:
        print(f"Group {group_name} not found.")

def delete_group():
    try:
        available_groups = os.listdir("groups")
        print("Available Groups to Delete:")
        for group in available_groups:
            print(f" - {group.replace('.json', '')}")
        print(" - Back")
    except FileNotFoundError:
        print("No groups found.")
        return

    group_name = input("Enter the name of the group to delete or 'Back' to return: ")
    if group_name.lower() == 'back':
        return

    confirmation = input(f"Are you sure you want to delete {group_name}? (yes/no): ")
    if confirmation.lower() == 'yes':
        try:
            os.remove(f"groups/{group_name}.json")
            print(f"Group {group_name} deleted successfully.")
        except FileNotFoundError:
            print(f"Group {group_name} not found.")


def groups_menu():
    while True:
        print("===== Groups Menu =====")
        print("1. Add Group")
        print("2. Edit Group")
        print("3. Delete Group")
        print("4. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            add_group()
        elif choice == "2":
            edit_group()
        elif choice == "3":
            delete_group()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")
