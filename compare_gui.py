# make simple tkinter gui to compare two lists

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import json

import main

BG_COLORS = {
    'red': '#FFAAAA',
    'green': '#AAFFAA',
    'yellow': '#FFFFAA',
    'white': '#FFFFFF',
}


class View(tk.Tk):
    def __init__(self):
        super().__init__()

        self.old_image = None
        self.new_image = None
        self.root_node = None
        self.top_list_items = []

        self.title("Compare Lists")
        self.geometry("800x800")
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.rowconfigure(10, weight=1)
        self.rowconfigure(12, weight=1)

        self.button_back = tk.Button(self, text="< Back", command=lambda: None)
        self.button_back.grid(row=0, column=2, columnspan=2, padx=3, pady=3, sticky="w")

        self.button_left = tk.Button(self, text="Load Old Image", command=lambda: self.add_new_image_file('left'))
        self.button_right = tk.Button(self, text="Load New Image", command=lambda: self.add_new_image_file('right'))
        self.button_left.grid(row=2, column=2, columnspan=2, padx=3, pady=3, sticky="nsew")
        self.button_right.grid(row=2, column=4, padx=3, pady=3, sticky="nsew")

        self.label_left = tk.Text(self, wrap="word", height=4, width=40)
        self.label_right = tk.Text(self, wrap="word", height=4, width=40)
        self.label_left.insert(tk.END, "Image 1: Nothing Loaded")
        self.label_right.insert(tk.END, "Image 2: Nothing Loaded")
        self.label_left.config(state="disabled")
        self.label_right.config(state="disabled")
        self.label_left.grid(row=3, column=2, columnspan=2, padx=3, pady=3, sticky="we")
        self.label_right.grid(row=3, column=4, padx=3, pady=3, sticky="we")

        self.label_path = tk.Label(self, text="Path: ", justify="left", font=("Helvetica", 12))
        self.label_path.grid(row=4, column=2, padx=3, pady=3, sticky="w")
        self.label_path_val = tk.Text(self, height=1, font=("Courier", 12))
        self.label_path_val.grid(row=4, column=3, columnspan=2, padx=3, pady=3, sticky="w")
        self.label_path_val.bind("<KeyRelease>", lambda e: self.set_cur_path(None))

        self.listbox_top = tk.Listbox(self, width=30, height=20, font=("Courier", 12), activestyle="none")
        self.listbox_top.grid(row=10, column=2, columnspan=3, padx=3, pady=3, sticky="nsew")
        self.listbox_top.bind("<Double-Button-1>", lambda e: self.listbox_top_double_click(e))

        self.label_list_left = tk.Label(self, text="Deleted Files:", justify="left", font=("Helvetica", 12))
        self.label_list_right = tk.Label(self, text="New Files:", justify="left", font=("Helvetica", 12))
        self.label_list_left.grid(row=11, column=2, columnspan=2, padx=3, sticky="w")
        self.label_list_right.grid(row=11, column=4, padx=3, sticky="w")

        self.listbox_left = tk.Listbox(self, width=30, height=20, font=("Helvetica", 12))
        self.listbox_right = tk.Listbox(self, width=30, height=20, font=("Helvetica", 12))
        self.listbox_left.grid(row=12, column=2, columnspan=2, padx=3, sticky="nsew")
        self.listbox_right.grid(row=12, column=4, padx=3, sticky="nsew")
        self.listbox_left.config(state="disabled")
        self.listbox_right.config(state="disabled")

    def add_new_image_file(self, side_str, file_path=None):
        if side_str == 'left':
            label = self.label_left
            image_str = 'old_image'
            prefix = 'Old Image: '
        elif side_str == 'right':
            label = self.label_right
            image_str = 'new_image'
            prefix = 'New Image: '
        else:
            assert False, "side_str must be 'left' or 'right'"
        if file_path is None:
            file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select File", filetypes=(("Json Files", "*.json"), ("All Files", "*.*")))
        if file_path == "":
            return
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                assert 'root' in data.keys(), 'root key not found'
                time = data.get('INFO', {}).get('timestamp', 'NO TIME FOUND')
                rootdir = data.get('INFO', {}).get('rootdir', 'NO ROOTDIR FOUND')
                label.config(state="normal")
                label.delete(1.0, tk.END)
                label.insert(tk.END, prefix + '\n' + 'Time:' + time + "\n" + rootdir)
                label.config(state="disabled")
                setattr(self, image_str, data)
            except Exception as e:
                messagebox.showwarning("Warning", "This file is not a valid json file. Reason: " + str(e))
                return
        if self.old_image is not None and self.new_image is not None:
            print('both images loaded')
            self.root_node = main.get_tree(self.old_image['root'], self.new_image['root'], root_name='.')
            self.set_cur_path('./')

    def listbox_top_double_click(self, event):
        ind = self.listbox_top.curselection()
        if len(ind) == 0:
            return
        ind = ind[0]
        print('listbox_top_double_click', ind)
        if ind == 0:
            parent = self.current_node.parent
            if parent is None:
                return
            self.set_cur_path(parent.full_name)
            return
        ind -= 1  # first element in listbox is parent
        if ind >= len(self.top_list_items):
            return
        item = self.top_list_items[ind]
        self.set_cur_path(item.full_name)

    def set_cur_path(self, path):
        print('set_cur_path', path)
        assert self.root_node is not None, 'root is None'
        if path is None:
            path = self.label_path_val.get(1.0, tk.END).strip()
        else:
            self.label_path_val.delete(1.0, tk.END)
            self.label_path_val.insert(tk.END, path)
        cur = self.root_node
        for part in path.replace('\\', '/').split('/'):  # split on / and \\
            if part == '' or part == '.':
                continue
            for child in cur.children:
                if child.name == part:
                    cur = child
                    break
            else:
                print('path not found')
                return
        self.current_node = cur
        self.top_list_items = sorted(self.current_node.children, key=lambda x: (1 if x.is_same() else 0, x.name))
        int_to_color = {
            3: BG_COLORS['yellow'],  # both new and old
            2: BG_COLORS['green'],  # only new
            1: BG_COLORS['red'],  # only old
            0: BG_COLORS['white'],  # same
        }
        top_lst = [(
                self.get_node_print_lint(chld),
                int_to_color[2 * chld.has_exclusive_new_content() + 1 * chld.has_exclusive_old_content()],
            ) for chld in self.top_list_items]
        del_files = self.current_node.old_files - self.current_node.new_files
        new_files = self.current_node.new_files - self.current_node.old_files
        self.set_listboxes(top_lst, del_files, new_files, add_parent=self.current_node.parent is not None)

    def set_listboxes(self, top, left, right, add_parent=True):
        self.listbox_left.config(state="normal")
        self.listbox_right.config(state="normal")
        self.listbox_top.delete(0, tk.END)
        self.listbox_left.delete(0, tk.END)
        self.listbox_right.delete(0, tk.END)
        top_ind = 0
        self.listbox_top.insert(tk.END, '<<< back' if add_parent else '')
        self.listbox_top.itemconfig(tk.END, bg=BG_COLORS['white'])
        top_ind += 1
        for item, color in top:
            self.listbox_top.insert(top_ind, item)
            self.listbox_top.itemconfig(top_ind, bg=color)
            top_ind += 1
        self.listbox_top.insert(tk.END, '')
        for i, item in enumerate(left):
            self.listbox_left.insert(i, item)
            self.listbox_left.itemconfig(i, bg=BG_COLORS['red'])
        for i, item in enumerate(right):
            self.listbox_right.insert(i, item)
            self.listbox_right.itemconfig(i, bg=BG_COLORS['green'])
        # self.listbox_left.config(state="disabled")
        # self.listbox_right.config(state="disabled")
        # self.listbox_left.configure({'disabledbackground': '#FFAAAA'})
        # self.listbox_right.configure(bg="#FFAAAA", fg="black")

    @staticmethod
    def get_node_print_lint(node):
        DEL_TEXT = '(DEL)'
        NEW_TEXT = '(NEW)'
        SAME_TEXT = '  SAME'
        if node.new_path is None:
            new_status = DEL_TEXT
        elif node.old_path is None:
            new_status = NEW_TEXT
        else:  # not new or old
            new_status = ' ' * len(DEL_TEXT)
        # add deep stats
        is_same = SAME_TEXT if node.is_same() else ' ' * len(SAME_TEXT)
        stats = [
            ('-D', node.stats_deep['dirs']['old_only']),
            ('-F', node.stats_deep['files']['old_only']),
            ('+D', node.stats_deep['dirs']['new_only']),
            ('+F', node.stats_deep['files']['new_only']),
        ]
        stats = [f'{s[0]}{n}{s[1]}' if n > 0 else '' for s, n in stats]
        
        return f'{new_status} {node.name:<20} {is_same} {stats[0]:>6} {stats[1]:>6} {stats[2]:>6} {stats[3]:>6}'





if __name__ == '__main__':
    view = View()
    frame = tk.Frame(view)
    # view.add_new_image_file('left', r'M:\MyFiles\Code\Python\Scripts\directory_tree_save_and_compare\temp1.json')
    # view.add_new_image_file('right', r'M:\MyFiles\Code\Python\Scripts\directory_tree_save_and_compare\temp2.json')
    view.add_new_image_file('left', r'M:\MyFiles\Code\Python\Scripts\directory_tree_save_and_compare\result_after_everything_ssd2tb.json')
    view.add_new_image_file('right', r'M:\MyFiles\Code\Python\Scripts\directory_tree_save_and_compare\result_night_after.json')
    view.mainloop()
