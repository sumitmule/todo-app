from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from pymongo import MongoClient
from datetime import datetime
from tkinter import simpledialog
import customtkinter
customtkinter.set_appearance_mode("dark")


# Connect to MongoDB database
client = MongoClient('mongodb://localhost:27017/')
db = client['todo_app']
collection = db['tasks']
collectiondone = db['donetask']

# Define the GUI class
class TodoApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
      
        self.title('To-Do App')
        self.geometry('700x700')
        self.resizable(True, True)

        # Create widgets
        self.task_label = customtkinter.CTkLabel(self, text='Task:', font=('Arial', 14))
        self.task_entry = customtkinter.CTkEntry(self, font=('Arial', 14), width=300, placeholder_text='Complete assignment ...')
        # self.tsk_l = customtkinter.CTkLabel(self, text="pending tasks",font=('Bold',16))
        self.priority_label = customtkinter.CTkLabel(self, text='Priority:', font=('Arial', 14))
        self.priority_entry = customtkinter.CTkEntry(self, font=('Arial', 14), placeholder_text='1, 2, 3 ...')
        self.due_date_label = customtkinter.CTkLabel(self, text='Due Date:', font=('Arial', 14))
        self.due_date_entry = customtkinter.CTkEntry(self, font=('Arial', 14), placeholder_text='dd/mm/yyyy')
        self.add_button = customtkinter.CTkButton(self, text='Add Task', font=('Arial', 14), command=self.add_task)
        self.task_listbox = Listbox(self, font=('Arial', 14), width=65, height=8)
        self.task_done_listbox = Listbox(self, font=('Arial', 14), width=65, height=8)
        self.edit_button = customtkinter.CTkButton(self, text='Edit Task', font=('Arial', 14), command=self.edit_task)
        self.delete_button = customtkinter.CTkButton(self, text='Delete Task', font=('Arial', 14), command=self.delete_task)
        self.mark_done_button = customtkinter.CTkButton(self, text='Mark as Done', font=('Arial', 14), command=self.mark_done_task)


        # Pack widgets
        self.task_label.place(relx=0.1, rely=0.08, anchor="w")
        self.task_entry.place(relx=0.3, rely=0.08, anchor="w")
        # self.task_
        self.priority_label.place(relx=0.1, rely=0.15, anchor="w")
        self.priority_entry.place(relx=0.3, rely=0.15, anchor="w")
        self.due_date_label.place(relx=0.1, rely=0.22, anchor="w")
        self.due_date_entry.place(relx=0.3, rely=0.22, anchor="w")
        self.add_button.place(relx=0.1, rely=0.33, anchor="w")
        self.task_listbox.place(relx=0.5, rely=0.40, anchor="n")
        self.task_done_listbox.place(relx=0.5, rely=0.65, anchor="n")
        self.edit_button.place(relx=0.1, rely=0.93, anchor="w")
        self.delete_button.place(relx=0.7, rely=0.93, anchor="w")
        self.mark_done_button.place(relx=0.4, rely=0.93, anchor="w")


        # Load existing tasks from database
        self.load_tasks()
        self.load_done_task()

    # Load existing tasks from database and display them in the listbox
    def load_tasks(self):
        self.task_listbox.delete(0, END)
        tasks = collection.find().sort('priority')
        for task in tasks:
            self.task_listbox.insert(END, f'{task["task"]}        ({task["priority"]})        Due: {task["due_date"]}')
    
    def load_done_task(self):
        self.task_done_listbox.delete(0, END)
        tasks = collectiondone.find()
        for task in tasks:
            self.task_done_listbox.insert(END, f'{task["task"]}        ({task["priority"]})        Due: {task["due_date"]}')


    # Add a new task to the database and update the listbox
    def add_task(self):

        task = self.task_entry.get()

        try:
            priority = int(self.priority_entry.get())
        except ValueError:
            messagebox.showwarning('Warning', 'Please enter a number in priority field.')
            return

        # try:
        due_date_str = self.due_date_entry.get()
        # except ValueError:
        #     messagebox.showwarning('Warning', 'Please enter the date in given format.')
        #     return


        if task and priority and due_date_str:

            try:
                due_date = datetime.strptime(due_date_str, '%d/%m/%Y')
            except ValueError:
                messagebox.showwarning('Warning', 'Please enter the date in given format.')
                return
            
            collection.insert_one({'task': task, 'priority': priority, 'due_date': due_date})
            self.load_tasks()
            self.task_entry.delete(0, END)
            self.priority_entry.delete(0, END)
            self.due_date_entry.delete(0, END)
        else:
            messagebox.showwarning('Warning', 'Please enter a task, priority, and due date.')

    # Edit the selected task in the database and update the listbox
    def edit_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            task = self.task_listbox.get(selection)
            task_name = task.split("(")[0].strip()
            new_task_ip = customtkinter.CTkInputDialog(text=f'Enter a new name for "{task_name}":', title="Edit Task")
            new_task = new_task_ip.get_input()
            if new_task:
                collection.update_one({'task': task_name}, {'$set': {'task': new_task}})
                self.load_tasks()
        else:
            messagebox.showwarning('Warning', 'Please select a task to edit.')

    # Delete the selected task from the database and update the listbox
    def delete_task(self):
        selection = self.task_listbox.curselection()
        selectiondone = self.task_done_listbox.curselection()
        if selection:
            task = self.task_listbox.get(selection)
            task_name = task.split("(")[0].strip()
            collection.delete_one({'task': task_name})
            self.load_tasks()
        elif selectiondone:
            task = self.task_done_listbox.get(selectiondone[0])
            task_name = task.split("(")[0].strip()
            collectiondone.delete_one({'task': task_name})
            self.load_done_task()
        else:
            messagebox.showwarning('Warning', 'Please select a task to delete.')

    def mark_done_task(self):
        selection = self.task_listbox.curselection()
        if selection:
            task = self.task_listbox.get(selection[0])
            task_name = task.split("(")[0].strip()
            tobemarked = collection.find_one({'task': task_name})
            collectiondone.insert_one({'task': tobemarked['task'], 'priority': tobemarked['priority'], 'due_date': tobemarked['due_date']})
            collection.delete_one({'task': task_name})
            self.load_tasks()
            self.load_done_task()
        else:
            messagebox.showwarning('Warning', 'Please select a task')

# Create the root window and run the application

app = TodoApp()
app.mainloop()