import configparser
import asana
from six import print_


def user_select_option(message, options):
    option_lst = list(options)
    print_(message)
    for i, val in enumerate(option_lst):
        print_(i, ': ' + val['name'])
    index = int(input("Enter choice (default 0): ") or 0)
    return option_lst[index]


def create_n_tasks_under_a_task(workspace, project, parent_task_id, num_sub_tasks, prefix):
    i = 1
    while i < num_sub_tasks + 1:
        print("task " + str(i))
        client.tasks.create_in_workspace(workspace['id'],
                                         {'name': prefix + str(i),
                                          'projects': [project['id']],
                                          'parent': parent_task_id
                                          }
                                         )
        i = i + 1


class AsanaAutomator:
    def __init__(self, client):
        self.client = client


def prompt_parent_nsubtask_prefix():
    parent_task_id = input("Enter parent task id:")
    num_sub_tasks = int(input("Enter number of tasks:") or 0)
    prefix = input("Enter the prefix for subtask:")

    return parent_task_id, num_sub_tasks, prefix


def create_n_tasks_under_all_subtask(client, workspace, project):
    parent_task_id, num_sub_tasks, prefix = prompt_parent_nsubtask_prefix()
    all_subtasks = client.tasks.find_all({'task': parent_task_id})
    print(all_subtasks.items)
    i = 0
    for subtask in all_subtasks.items:
        create_n_tasks_under_a_task(workspace, project, subtask['id'], num_sub_tasks, prefix)
        print("subtask processed: " + str(i))
        i = i + 1


def add_project_to_subtask(client, workspace, task_id):
    all_subtasks = client.tasks.find_all({'task': task_id})


def create_n_tasks_under_a_task_(client, workspace, project):
    parent_task_id, num_sub_tasks, prefix = prompt_parent_nsubtask_prefix()

    create_n_tasks_under_a_task(client, workspace, project, parent_task_id, num_sub_tasks, prefix)


def get_access_key():
    config = configparser.ConfigParser()
    config.readfp(open(r'/Users/kchandra/Lyf/Syncs/Dropbox/AppsMisc/ApiKeys/asana-personal-key.txt'))
    access_key = config.get('SECTION', 'PERSONAL_ACCESS_TOKEN')
    return access_key


def main():
    access_key = get_access_key()
    client = asana.Client.access_token(access_key)
    workspaces = client.workspaces.find_all()

    workspace = user_select_option("Please choose a workspace", workspaces)
    projects = client.projects.find_all({'workspace': workspace['id']})
    project = user_select_option("Please choose a project", projects)

    print("What you want to do next?")
    print("1. You want to create set of tasks under a task")
    print("2. You want to create set of tasks under all subtasks")

    option = input("Enter the input:")

    if option is "1":
        create_n_tasks_under_a_task_(workspace, project)
    elif option is "2":
        create_n_tasks_under_all_subtask(workspace, project)


if __name__ == '__main__':
# main()
