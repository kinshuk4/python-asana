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


class AsanaAutomator:
    def __init__(self, client):
        self.client = client
    def move_tasks_from_today_to_later(self, workspace, project):
        mytasks = self.client.tasks.find_all()
    def create_n_tasks_under_a_task(self, workspace, project, parent_task_id, num_sub_tasks, prefix):
        i = 1
        while i < num_sub_tasks + 1:
            print("task " + str(i))
            self.client.tasks.create_in_workspace(workspace['id'],
                                                  {'name': prefix + str(i),
                                                   'projects': [project['id']],
                                                   'parent': parent_task_id
                                                   }
                                                  )
            i = i + 1

    def prompt_parent_nsubtask_prefix(self):
        parent_task_id = input("Enter parent task id:")
        num_sub_tasks = int(input("Enter number of tasks:") or 0)
        prefix = input("Enter the prefix for subtask:")

        return parent_task_id, num_sub_tasks, prefix

    def create_n_tasks_under_all_subtask(self, workspace, project):
        parent_task_id, num_sub_tasks, prefix = self.prompt_parent_nsubtask_prefix()
        all_subtask = self.client.tasks.subtasks(parent_task_id)
        print(all_subtask)
        i = 0
        for subtask in all_subtask:
            i = i + 1
            print("subtask processed: " + str(i))
            if i < 253:
                continue
            print(subtask)
            self.create_n_tasks_under_a_task(workspace, project, subtask['id'], num_sub_tasks, prefix)



    def add_project_to_subtask(self, workspace, project):
        task_id = input("Enter parent task id:")
        all_subtask = self.client.tasks.subtasks(task_id)

        for subtask in all_subtask:
            print(subtask['id'])
            self.client.tasks.add_project(subtask['id'], {
                'project': project['id']
            })

    def update_date_to_all_subtask(self, workspace, project):
        task_id = input("Enter parent task id:")
        all_subtask = self.client.tasks.subtasks(task_id)
        date_text = input("Enter the date(0 for removing it i.e. setting to null): ")
        if date_text is '0':
            date = None
        else:
            date = get_date_in_is8601_from_text(date_text)

        for subtask in all_subtask:
            print(subtask['id'])
            self.client.tasks.update(subtask['id'], {
                'due_at': date
            })

    def create_n_tasks_under_a_task_(self, workspace, project):
        parent_task_id, num_sub_tasks, prefix = self.prompt_parent_nsubtask_prefix()

        self.create_n_tasks_under_a_task(workspace, project, parent_task_id, num_sub_tasks, prefix)



def get_access_key():
    config = configparser.ConfigParser()
    config.readfp(open(r'/Users/kchandra/Lyf/Syncs/Dropbox/AppsMisc/ApiKeys/asana-personal-key.txt'))
    access_key = config.get('SECTION', 'PERSONAL_ACCESS_TOKEN')
    return access_key

def get_date_in_is8601_from_text(text='Thu, 16 Dec 2010 12:14:05 +0000'):
    import dateutil.parser as parser
    date = parser.parse(text)
    return date.isoformat()

def main():
    access_key = get_access_key()
    client = asana.Client.access_token(access_key)
    asanaAutomator = AsanaAutomator(client)
    workspaces = client.workspaces.find_all()

    workspace = user_select_option("Please choose a workspace", workspaces)
    projects = client.projects.find_all({'workspace': workspace['id']})
    project = user_select_option("Please choose a project", projects)

    print("What you want to do next?")
    print("1. You want to create set of tasks under a task")
    print("2. You want to create set of tasks under all subtasks")
    print("3. Add all subtasks of task to a project")
    print("4. Update due date in all subtasks")

    option = input("Enter the input:")

    if option is "1":
        asanaAutomator.create_n_tasks_under_a_task_(workspace, project)
    elif option is "2":
        asanaAutomator.create_n_tasks_under_all_subtask(workspace, project)
    elif option is "3":
        asanaAutomator.add_project_to_subtask(workspace, project)
    elif option is "4":
        asanaAutomator.update_date_to_all_subtask(workspace, project)


if __name__ == '__main__':
    main()
