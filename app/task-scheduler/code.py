import os

from TaskScheduler import TaskScheduler

# replace 'path\\to\\your\\xml\\file.xml' with the path to your XML file
xml_file_path = 'path\\to\\your\\xml\\file.xml'
# create a Task Scheduler object
ts = TaskScheduler()
# create a task registration object
task_reg = ts.NewTaskRegistration()
# load the task from the XML file
task_reg.XmlText = open(xml_file_path, 'r').read()
# register the task with the Task Scheduler
task_name = os.path.basename(xml_file_path).split(
    '.')[0]  # use the XML file name as the task name
ts.RegisterTask(task_name, task_reg)
print('Task added to the Windows Task Scheduler.')
