# make simple tkinter gui to compare two lists

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os

# create window
window = tk.Tk()
window.title("Compare Lists")
window.geometry("500x500")

# create frame
frame = tk.Frame(window)
frame.pack()

# create label
label = tk.Label(frame, text="Compare Lists")
label.grid(row=0, column=0, columnspan=2)

# create listbox
listbox1 = tk.Listbox(frame, width=30, height=20)
listbox1.grid(row=1, column=0, padx=10, pady=10)

listbox2 = tk.Listbox(frame, width=30, height=20)
listbox2.grid(row=1, column=1, padx=10, pady=10)

lst1 = ['a', 'b', 'c', 'd', 'e']
lst2 = ['a', 'b', 'c', 'd']

for item in lst1:
    listbox1.insert(tk.END, item)

for item in lst2:
    listbox2.insert(tk.END, item)

# create buttons
button1 = tk.Button(frame, text="Add List 1", command=lambda: add_list(listbox1))
button1.grid(row=2, column=0, padx=10, pady=10)

button2 = tk.Button(frame, text="Add List 2", command=lambda: add_list(listbox2))
button2.grid(row=2, column=1, padx=10, pady=10)

button3 = tk.Button(frame, text="Compare Lists", command=lambda: compare_lists(listbox1, listbox2))
button3.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# create functions
def add_list(listbox):
    file = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    with open(file, "r") as f:
        for line in f:
            listbox.insert(tk.END, line.strip())

def compare_lists(listbox1, listbox2):
    list1 = listbox1.get(0, tk.END)
    list2 = listbox2.get(0, tk.END)
    for item in list1:
        if item not in list2:
            listbox1.itemconfig(listbox1.get(0, tk.END).index(item), bg="red")
    for item in list2:
        if item not in list1:
            listbox2.itemconfig(listbox2.get(0, tk.END).index(item), bg="red")

# run main loop
window.mainloop()
