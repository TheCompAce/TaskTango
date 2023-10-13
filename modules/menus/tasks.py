import json
import os

def add_task():
    # Gather information for a new task
    task_info = {}
    task_info['taskName'] = input('Enter the name of the task: ')
    task_info['description'] = input('Enter the description of the task: ')
    task_info['createdBy'] = input('Enter the identifier for the creator: ')
    task_info['groups'] = input('Enter the groups involved (comma-separated): ').split(',')
    task_info['systemPrompt'] = input('Enter the system prompt for the task: ')
    task_info['dependencies'] = input('Enter any dependencies (comma-separated, leave empty if none): ').split(',')
    task_info['completionIndicators'] = input('Enter completion indicators (comma-separated): ').split(',')
    task_info['dynamicAllocation'] = input('Enable dynamic allocation? (yes/no): ').lower() == 'yes'
    
    # Convert 'variables' to dictionary
    variables_str = input('Enter custom variables as key=value pairs separated by commas (e.g., var1=val1,var2=val2): ')
    task_info['variables'] = {}
    if variables_str:
        for pair in variables_str.split(','):
            key, value = pair.split('=')
            task_info['variables'][key] = value

    # Save the task information to a JSON file
    task_file_path = os.path.join('tasks', 'task_configs', f"{task_info['taskName']}.json")
    with open(task_file_path, 'w') as f:
        json.dump(task_info, f, indent=4)

def edit_task():
    # List available tasks for editing
    task_files = os.listdir(os.path.join('tasks', 'task_configs'))
    print('Available tasks for editing:')
    for idx, task_file in enumerate(task_files):
        print(f"{idx+1}. {task_file[:-5]}")
    choice = input('Select a task to edit (by number) or type \'back\' to go back: ')
    if choice.lower() == 'back':
        return
    selected_task_file = task_files[int(choice) - 1]
    
    # Load the selected task's configuration
    task_file_path = os.path.join('tasks', 'task_configs', selected_task_file)
    with open(task_file_path, 'r') as f:
        task_info = json.load(f)
        
    # Edit the task's configuration
    for key in task_info.keys():
        new_value = input(f"Current {key}: {task_info[key]} -- Enter new value (or press Enter to keep current): ")
        if new_value:
            task_info[key] = new_value if key != 'groups' else new_value.split(',')
            
    # Save the edited task configuration
    with open(task_file_path, 'w') as f:
        json.dump(task_info, f, indent=4)

def delete_task():
    # List available tasks for deletion
    task_files = os.listdir(os.path.join('tasks', 'task_configs'))
    print('Available tasks for deletion:')
    for idx, task_file in enumerate(task_files):
        print(f"{idx+1}. {task_file[:-5]}")
    choice = input('Select a task to delete (by number) or type \'back\' to go back: ')
    if choice.lower() == 'back':
        return
    selected_task_file = task_files[int(choice) - 1]
    
    # Confirm before deletion
    confirm = input(f"Are you sure you want to delete {selected_task_file[:-5]}? (yes/no): ")
    if confirm.lower() == 'yes':
        os.remove(os.path.join('tasks', 'task_configs', selected_task_file))
        print('Task deleted successfully.')
    else:
        print('Deletion cancelled.')

def task_menu():
    while True:
        print('===== Task Menu =====')
        print('1. Add Task')
        print('2. Edit Task')
        print('3. Delete Task')
        print('4. Back')
        choice = input('Please choose an option: ')
        
        if choice == '1':
            add_task()
        elif choice == '2':
            edit_task()
        elif choice == '3':
            delete_task()
        elif choice == '4':
            return  # Go back to the previous menu
        else:
            print('Invalid choice. Please try again.')
