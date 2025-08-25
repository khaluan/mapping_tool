import tkinter as tk
from tkinter import messagebox, filedialog
from response import parse_output, parse_mapping
from graph import to_graph, insert_mapping

WIDTH = 100

def create_node_label(node):
    """
    Create a label for a node with its name and shape.
    :param node: Node object with 'name' and 'shape' attributes.
    :return: Formatted string label.
    """
    label_map = {'box': 'Entity', 'ellipse': 'Process', 'cylinder': 'Datastore', 'rectangle': 'Entity'}
    name = node['label'] if 'label' in node else node['name']
    shape = node['shape'] if 'shape' in node else 'ellipse'
    return f"{name} ({label_map[shape]})" 


class MappingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mapping Selector")

        self.mapping = []

        # Default sample data
        self.all_left_items = ['Please select a response file to load the constructed graph']
        self.all_right_items = ['Please select a response file to load the ground truth graph']

        # Active items
        self.left_items = self.all_left_items.copy()
        self.right_items = self.all_right_items.copy()

        # --- UI Layout ---

        # Left listbox
        self.left_label = tk.Label(root, text=f"Constructed Nodes")
        self.left_label.grid(row=0, column=0)
        self.left_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, exportselection=False, width=WIDTH)
        self.left_listbox.grid(row=1, column=0)
        self.update_listbox(self.left_listbox, self.left_items)
        self.left_listbox.bind('<<ListboxSelect>>', self.left_listbox_select)

        # Right listbox
        self.right_label = tk.Label(root, text=f"Ground Truth Nodes")
        self.right_label.grid(row=0, column=2)
        self.right_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, exportselection=False, width=WIDTH)
        self.right_listbox.grid(row=1, column=2)
        self.update_listbox(self.right_listbox, self.right_items)
        self.right_listbox.bind('<<ListboxSelect>>', self.right_listbox_select)

        # Add Button
        self.add_button = tk.Button(root, text="Add →", command=self.add_mapping)
        self.add_button.grid(row=1, column=1, padx=10)

        # Mapping display
        self.mapping_label = tk.Label(root, text="Selected Mappings")
        self.mapping_label.grid(row=5, column=0, columnspan=3)
        self.mapping_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=WIDTH)
        self.mapping_listbox.grid(row=6, column=0, columnspan=3, pady=5)

        # Remove button
        self.remove_button = tk.Button(root, text="Remove", command=self.remove_mapping)
        self.remove_button.grid(row=5, column=2)

        # File input
        self.filename_label = tk.Label(root, text="File Name:")
        self.filename_label.grid(row=7, column=0, sticky='e')
        self.filename_entry = tk.Entry(root)
        self.filename_entry.grid(row=7, column=1, columnspan=1)
        self.save_button = tk.Button(root, text="Save", command=self.save_to_file)
        self.save_button.grid(row=7, column=2)
        
        # Load buttons
        self.load_left_button = tk.Button(root, text="Load constructed graph from file", command=self.load_left_items)
        self.load_left_button.grid(row=8, column=0, pady=5)

        self.load_right_button = tk.Button(root, text="Load ground truth from file", command=self.load_right_items)
        self.load_right_button.grid(row=8, column=2, pady=5)

        # Shape selector
        self.shape_label = tk.Label(root, text="Shape Type")
        self.shape_label.grid(row=0, column=3)
        self.shape_var = tk.StringVar()
        self.shape_var.set("Process")  # default
        self.shape_menu = tk.OptionMenu(root, self.shape_var, "Process", "Entity", "Datastore")
        self.shape_menu.grid(row=1, column=3)

        self.left_selected_label = tk.Label(root, text="Selected Constructed Mapping")
        self.left_selected_label.grid(row=3, column=0)
        self.left_selected_text = tk.Text(root, height=4, width=int(WIDTH * 0.75))
        self.left_selected_text.grid(row=4, column=0)

        self.right_selected_label = tk.Label(root, text="Selected GT Mapping")
        self.right_selected_label.grid(row=3, column=2)
        self.right_selected_text = tk.Text(root, height=4, width=int(WIDTH * 0.75))
        self.right_selected_text.grid(row=4, column=2)

    

    def update_listbox(self, listbox, items):
        listbox.delete(0, tk.END)
        for item in items:
            listbox.insert(tk.END, item)

    def add_mapping(self):
        left_indices = self.left_listbox.curselection()
        right_indices = self.right_listbox.curselection()

        shape_mapping = {"Process": "ellipse", "Entity": "box", "Datastore": "cylinder"}
        shape = self.shape_var.get()
        shape = shape_mapping[shape]

        selected_left = [self.left_item_key[self.left_items[i]] for i in left_indices]
        selected_left_shape = [self.left_dfd.nodes[item]["shape"] for item in selected_left]

        selected_right = [self.right_item_key[self.right_items[i]] for i in right_indices]
        selected_right_shape = [self.right_dfd.nodes[item]["shape"] for item in selected_right]
        
        shapes = set(selected_left_shape + selected_right_shape)
        if shape not in shapes:
            messagebox.showwarning("Shape Mismatch", "Selected items must have the same shape type.")
            return
        
        if len(shapes) > 1 and shapes != set(['cylinder', 'ellipse']):
            print(shapes)
            messagebox.showwarning("Shape Mismatch", "Merging multiple shapes is not allowed.")

        if not selected_left and not selected_right:
            messagebox.showwarning("Selection Error", "Please select at least one item from either list.")
            return
        
        pair = {"left": selected_left, "right": selected_right, "shape": shape}

        if pair not in self.mapping:
            self.mapping.append(pair)
            self.mapping_listbox.insert(tk.END, f"{pair}")

        # Remove selected items
        self.left_items = [item for item in self.left_items if self.left_item_key[item]  not in selected_left]
        self.right_items = [item for item in self.right_items if self.right_item_key[item] not in selected_right]

        self.update_listbox(self.left_listbox, self.left_items)
        self.update_listbox(self.right_listbox, self.right_items)

    def remove_mapping(self):
        selection = self.mapping_listbox.curselection()
        if not selection:
            messagebox.showwarning("Remove Error", "Please select a mapping to remove.")
            return

        index = selection[0]
        pair = self.mapping.pop(index)
        self.mapping_listbox.delete(index)

        # Restore items
        # TODO: 
        for item in pair["left"]:
            self.left_items.append(self.left_item_rkey[item])
        for item in pair["right"]:
            self.right_items.append(self.right_item_rkey[item])

        self.left_items.sort()
        self.right_items.sort()
        self.update_listbox(self.left_listbox, self.left_items)
        self.update_listbox(self.right_listbox, self.right_items)

    def save_to_file(self):
        filename = self.filename_entry.get().strip()
        if not filename:
            messagebox.showerror("Filename Error", "Please enter a valid filename.")
            return
        if not filename.endswith(".py"):
            filename += ".py"

        final_mapping = self.mapping.copy()

        # Add remaining unmapped items
        for item in self.left_items:
            final_mapping.append({"left": [self.left_item_key[item]], "right": [], "shape": self.left_dfd.nodes[self.left_item_key[item]]["shape"]})
        for item in self.right_items:
            final_mapping.append({"left": [], "right": [self.right_item_key[item]], "shape": self.right_dfd.nodes[self.right_item_key[item]]["shape"]})

        try:
            with open(filename, 'w') as f:
                f.write("mapping = [\n")
                for item in final_mapping:
                    f.write(f"    {item},\n")
                f.write("]\n")
            messagebox.showinfo("Success", f"Mapping saved to '{filename}'")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file: {e}")

    def load_left_items(self):
        file_path = filedialog.askopenfilename(title="Select file for Left Items")
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                response = f.read()
                dfd = to_graph(parse_output(response))
                mapping = parse_mapping(response)
                dfd = insert_mapping(dfd, mapping)
                self.left_item_key = {create_node_label(dfd.nodes[node]):node for node in dfd.nodes()}                
                self.left_item_rkey = {node:create_node_label(dfd.nodes[node]) for node in dfd.nodes()}
                self.left_items = [create_node_label(dfd.nodes[node]) for node in dfd.nodes()]
                self.left_dfd = dfd
                self.left_items.sort()

                self.update_listbox(self.left_listbox, self.left_items)
        except Exception as e:
            print(e)
            messagebox.showerror("Load Error", f"Failed to load left items: {e}")

    def load_right_items(self):
        file_path = filedialog.askopenfilename(title="Select file for Right Items")
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                response = f.read()
                dfd = to_graph(response)
                self.right_dfd = dfd
                self.right_item_key = {create_node_label(dfd.nodes[node]):node for node in dfd.nodes()}
                self.right_item_rkey = {node:create_node_label(dfd.nodes[node]) for node in dfd.nodes()}
                self.right_items = [create_node_label(dfd.nodes[node]) for node in dfd.nodes()]
                self.right_items.sort()
                self.update_listbox(self.right_listbox, self.right_items)
        except Exception as e:
            print(e)
            messagebox.showerror("Load Error", f"Failed to load right items: {e}")

    def left_listbox_select(self, event):
        selected_indices = self.left_listbox.curselection()
        if not selected_indices:
            self.left_selected_text.delete(1.0, tk.END)
            return
        node = self.left_items[selected_indices[-1]]
        node = self.left_item_key[node]
        selected_items = self.left_dfd.nodes[node]['mapping'] if 'mapping' in self.left_dfd.nodes[node] else "No mapping"
        self.left_selected_text.delete(1.0, tk.END)
        self.left_selected_text.insert(tk.END, selected_items)

    def right_listbox_select(self, event):
        selected_indices = self.right_listbox.curselection()
        if not selected_indices:
            self.right_selected_text.delete(1.0, tk.END)
            return
        node = self.right_items[selected_indices[-1]]
        node = self.right_item_key[node]
        selected_items = self.right_dfd.nodes[node]['mapping'] if 'mapping' in self.right_dfd.nodes[node] else "No mapping"
    
        self.right_selected_text.delete(1.0, tk.END)
        self.right_selected_text.insert(tk.END, selected_items)
    

if __name__ == "__main__":
    root = tk.Tk()
    app = MappingApp(root)
    root.mainloop()
