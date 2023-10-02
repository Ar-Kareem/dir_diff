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
class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, compare_settings):
        super().__init__(parent)
        self.title("Settings")
        self.compare_settings = compare_settings
        
        self.size_var = tk.BooleanVar(value=compare_settings['size'])
        self.mtime_var = tk.BooleanVar(value=compare_settings['mtime'])
        size_checkbox = tk.Checkbutton(self, text="Size", variable=self.size_var)
        size_checkbox.pack()
        mtime_checkbox = tk.Checkbutton(self, text="Modification Time", variable=self.mtime_var)
        mtime_checkbox.pack()
        save_button = tk.Button(self, text="Save", command=self.save_settings)
        save_button.pack()
        
    def save_settings(self):
        self.compare_settings['size'] = self.size_var.get()
        self.compare_settings['mtime'] = self.mtime_var.get()
        self.destroy()


class FileFolderSelectionGUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("File/Folder Selection")

        # Create buttons for selecting file and folder
        self.select_file_button = tk.Button(self, text="Select File", command=self.select_file)
        self.select_file_button.pack()

        self.select_folder_button = tk.Button(self, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack()

        # Initialize selected path as None
        self.selected_path = None

    def select_file(self):
        file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select File", filetypes=(("Json Files", "*.json"), ("All Files", "*.*")))
        if file_path:
            self.selected_path = file_path
            self.destroy()

    def select_folder(self):
        folder_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Folder")
        if folder_path:
            self.selected_path = folder_path
            self.destroy()


class View(tk.Tk):
    def __init__(self):
        super().__init__()

        self.compare_settings = {'size': True, 'mtime': True}

        self.old_image = None
        self.new_image = None
        self.root_node = None
        self.top_list_items = []
        self.current_node = None
        self.path_history = []
        self.path_history_ind = -1

        self.title("Compare Lists")
        self.geometry("800x800")
        self.resizable(True, True)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.rowconfigure(10, weight=1)
        # self.rowconfigure(12, weight=1)

        self.bind("<Button-4>", lambda e: self.on_back_button())
        self.bind("<Button-5>", lambda e: self.on_forward_button())

        self.button_back = tk.Button(self, text="<", command=lambda: messagebox.showwarning("Warning", "NANI ?!"))
        self.button_back.grid(row=0, column=1, columnspan=2, padx=3, pady=3, sticky="w")
        self.settings_back = tk.Button(self, text="Settings", command=self.open_settings)
        self.settings_back.grid(row=0, column=2, columnspan=2, padx=3, pady=3, sticky="w")
        self.create_new_image_button = tk.Button(self, text="Create New Image", command=lambda: self.create_new_image())
        self.create_new_image_button.grid(row=0, column=4, columnspan=2, padx=3, pady=3, sticky="e")

        self.button_left = tk.Button(self, text="Load Old Image", command=lambda: self.add_new_image_file('left'))
        self.button_right = tk.Button(self, text="Load New Image", command=lambda: self.add_new_image_file('right'))
        self.button_left.grid(row=2, column=2, columnspan=2, padx=3, pady=3, sticky="nsew")
        self.button_right.grid(row=2, column=4, columnspan=2, padx=3, pady=3, sticky="nsew")

        self.label_left = tk.Text(self, wrap="word", height=4, width=40)
        self.label_right = tk.Text(self, wrap="word", height=4, width=40)
        self.label_left.insert(tk.END, "Image 1: Nothing Loaded")
        self.label_right.insert(tk.END, "Image 2: Nothing Loaded")
        self.label_left.config(state="disabled")
        self.label_right.config(state="disabled")
        self.label_left.grid(row=3, column=2, columnspan=2, padx=3, pady=3, sticky="we")
        self.label_right.grid(row=3, column=4, columnspan=2, padx=3, pady=3, sticky="we")

        self.label_path = tk.Label(self, text="Path: ", justify="left", font=("Helvetica", 12))
        self.label_path.grid(row=4, column=2, padx=3, pady=3, sticky="w")
        self.label_path_val = tk.Text(self, height=1, font=("Courier", 12))
        self.label_path_val.grid(row=4, column=3, columnspan=2, padx=3, pady=3, sticky="w")
        self.label_path_val.bind("<KeyRelease>", lambda e: self.set_cur_path(None))

        self.listbox_top = tk.Listbox(self, width=30, height=20, font=("Courier", 12), activestyle="none")
        scrollbar_top = tk.Scrollbar(self, command=self.listbox_top.xview, orient=tk.HORIZONTAL)
        self.listbox_top.config(xscrollcommand=scrollbar_top.set)
        self.listbox_top.grid(row=10, column=2, columnspan=3, padx=3, pady=3, sticky="nsew")
        scrollbar_top.grid(row=11, column=2, columnspan=3, sticky="nsew")
        self.listbox_top.bind("<Double-Button-1>", lambda e: self.listbox_top_double_click(e))

        self.label_list_left = tk.Label(self, text="Deleted Files:", justify="left", font=("Helvetica", 12))
        self.label_list_right = tk.Label(self, text="New Files:", justify="left", font=("Helvetica", 12))
        self.label_list_left.grid(row=14, column=2, columnspan=2, padx=3, sticky="w")
        self.label_list_right.grid(row=14, column=4, columnspan=2, padx=3, sticky="w")

        self.listbox_left = tk.Listbox(self, width=30, height=5, font=("Helvetica", 12))
        self.listbox_right = tk.Listbox(self, width=30, height=5, font=("Helvetica", 12))
        scrollbar_left = tk.Scrollbar(self, command=self.listbox_left.yview)
        scrollbar_right = tk.Scrollbar(self, command=self.listbox_right.yview)
        self.listbox_left.config(yscrollcommand=scrollbar_left.set)
        self.listbox_right.config(yscrollcommand=scrollbar_right.set)
        self.listbox_left.grid(row=17, column=2, columnspan=2, padx=3, sticky="nsew")
        self.listbox_right.grid(row=17, column=4, columnspan=2, padx=3, sticky="nsew")
        scrollbar_left.grid(row=17, column=1, sticky="nsew")
        scrollbar_right.grid(row=17, column=5, sticky="nsew")
        self.listbox_left.config(state="disabled")
        self.listbox_right.config(state="disabled")
        # scrollbar.config(command=self.on_scroll)

    def on_scroll(self, *args):
        self.listbox_left.yview(*args)
        self.listbox_right.yview(*args)

    def open_settings(self):
        settings_window = SettingsWindow(self, self.compare_settings)
        settings_window.grab_set()
        self.wait_window(settings_window)
        if self.old_image is not None and self.new_image is not None:
            self.current_node = None  # otherwise it will not refresh the view
            self.rebuild_tree_and_view(self.cur_path_str, add_to_history=False)

    def add_new_image_file(self, side_str, file_folder_path=None):
        if side_str == 'left':
            label = self.label_left
            image_str = 'old_image'  # self.old_image
            prefix = 'Old Image: '
        elif side_str == 'right':
            label = self.label_right
            image_str = 'new_image'  # self.new_image
            prefix = 'New Image: '
        else:
            assert False, "side_str must be 'left' or 'right'"
        if file_folder_path is None:
            file_folder_gui = FileFolderSelectionGUI(self)
            self.wait_window(file_folder_gui)
            file_folder_path = file_folder_gui.selected_path
        if file_folder_path is None or file_folder_path == "":
            return
        # read path
        if os.path.isdir(file_folder_path):
            print(file_folder_path)
            data = main.get_directory_structure_v2(file_folder_path)
        elif os.path.isfile(file_folder_path):
            with open(file_folder_path, "r") as f:
                data = f.read()
        else:
            raise NotImplementedError("Not a valid file or folder")
        try:
            data = json.loads(data) if isinstance(data, str) else data
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
            if not hasattr(self, 'cur_path_str'):  # first time loading
                path_str = './'
                add_to_history=True
            else:  # if already loaded
                self.current_node = None
                path_str = self.cur_path_str
                add_to_history=False
            self.rebuild_tree_and_view(path_str, add_to_history=add_to_history)

    def rebuild_tree_and_view(self, path=None, add_to_history=True):
        assert self.old_image is not None and self.new_image is not None, 'both images not loaded'
        self.root_node = main.get_tree(self.old_image['root'], self.new_image['root'], compare_settings=self.compare_settings, root_name='.')
        self.set_cur_path(path, add_to_history=add_to_history)
        if self.root_node.stats_deep['dirs']['common'] == 0 and self.root_node.stats_deep['files']['common'] == 0:
            messagebox.showwarning("Warning", "No common files or directories found. \nThe two images are not related.")

    def listbox_top_double_click(self, event):
        ind = self.listbox_top.curselection()
        if len(ind) == 0:
            return
        ind = ind[0]
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

    def set_cur_path(self, path, add_to_history=True):
        assert self.root_node is not None, 'root is None'
        if path is None:
            path = self.label_path_val.get(1.0, tk.END).strip()
        else:
            self.label_path_val.delete(1.0, tk.END)
            self.label_path_val.insert(tk.END, path)
        self.cur_path_str = path
        cur = self.root_node
        for part in path.replace('\\', '/').split('/'):  # split on / and \\
            if part == '' or part == '.':
                continue
            for child in cur.children:
                if child.name == part:
                    cur = child
                    break
            else:
                return
        if self.current_node == cur:
            return
        self.current_node = cur
        if add_to_history:
            self.path_history = self.path_history[:self.path_history_ind + 1]
            self.path_history.append(self.current_node.full_name)
            self.path_history_ind = len(self.path_history) - 1
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
        deleted_files, new_files, common_files = self.current_node.get_del_new_common_file_splits() # deleted and newly created files
        self.set_listboxes(top_lst, deleted_files, new_files, add_parent=self.current_node.parent is not None)

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
        self.listbox_left.config(bg=BG_COLORS['red' if len(left) > 0 else 'white'], fg="black")
        self.listbox_right.config(bg=BG_COLORS['green' if len(right) > 0 else 'white'], fg="black")
        self.listbox_left.config(height=min(10, max(5, len(left))) + 1)
        self.listbox_right.config(height=min(10, max(5, len(right))) + 1)
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

    def create_new_image(self):
        folder_selected = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Folder to save as New Image")
        if folder_selected == "":
            return
        # print(folder_selected)
        new_dict = main.get_directory_structure_v2(folder_selected)
        default_name = os.path.basename(folder_selected) + '.json'
        save_path = filedialog.asksaveasfilename(
            initialdir=os.getcwd(),
            title="Select File",
            filetypes=(("Json Files", "*.json"), ("All Files", "*.*")),
            defaultextension='.json',
            initialfile=default_name)
        if save_path == "":
            return
        with open(save_path, 'w') as json_file:
            json.dump(new_dict, json_file, indent=2)
        messagebox.showinfo("Success", "New image created successfully")

    def on_back_button(self):
        if self.path_history_ind > 0:
            self.path_history_ind -= 1
            self.set_cur_path(self.path_history[self.path_history_ind], add_to_history=False)

    def on_forward_button(self):
        if self.path_history_ind < len(self.path_history) - 1:
            self.path_history_ind += 1
            self.set_cur_path(self.path_history[self.path_history_ind], add_to_history=False)


if __name__ == '__main__':
    view = View()
    frame = tk.Frame(view)
    # view.add_new_image_file('left', r'M:\MyFiles\Code\Python\Scripts\directory_tree_save_and_compare\jsons\new1.json')
    # view.add_new_image_file('right', r'M:\MyFiles\Code\Python\Scripts\directory_tree_save_and_compare\jsons\new2.json')
    # view.add_new_image_file('left', r'M:\MyFiles\Code\Python\Scripts\directory_tree_save_and_compare\jsons\result_after_everything_ssd2tb.json')
    # view.add_new_image_file('right', r'M:\MyFiles\Code\Python\Scripts\directory_tree_save_and_compare\jsons\result_night_after.json')
    view.mainloop()
