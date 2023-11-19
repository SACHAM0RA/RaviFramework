import tkinter as tk

button_color = "#%02x%02x%02x" % (200, 200, 200)

elements = []


def remove_element_clicked(element):
    elements.remove(element)
    element.pack_forget()


def apply_element_clicked(name, imp):
    print(name + " - " + imp)


def add_element_clicked():
    newElement = generateElementWidget(app)
    elements.append(newElement)


def generateElementWidget(master):
    container = tk.Frame(master, width=350, height=100)
    container.pack_propagate(False)
    container.pack(side=tk.TOP, anchor=tk.N, padx=5, pady=5)

    input_container = tk.Frame(container)
    input_container.pack(anchor=tk.NW, side=tk.LEFT)

    name_container = tk.Frame(input_container, relief=tk.GROOVE, borderwidth=2)
    name_container.pack(expand=True, fill=tk.BOTH)

    name_label = tk.Label(name_container, text="Name")
    name_label.pack(side=tk.LEFT)

    name_entry = tk.Entry(name_container, font=("Consolas", 10))
    name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    imp_container = tk.Frame(input_container, relief=tk.GROOVE, borderwidth=2)
    imp_container.pack(expand=True, fill=tk.BOTH)

    imp_label = tk.Label(imp_container, text="Implementation")
    imp_label.pack(side=tk.TOP, anchor=tk.NW)

    imp_text = tk.Text(imp_container, font=("Consolas", 10), height=3, width=40)
    imp_text.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    button_container = tk.Frame(container, relief=tk.GROOVE, borderwidth=2)
    button_container.pack(anchor=tk.NW, side=tk.LEFT, fill=tk.X, expand=True)

    apply_button = tk.Button(button_container, text="Apply", bg=button_color,
                             command=lambda: apply_element_clicked(name_entry.get(),imp_text.get("1.0", "end-1c")))
    apply_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    remove_button = tk.Button(button_container, text="Remove", bg=button_color,
                              command=lambda: remove_element_clicked(container))
    remove_button.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

    return container


# Create the main application window
app = tk.Tk()
app.title("RAVI GUI")

container = tk.Frame(app, width=350, height=60, relief=tk.GROOVE, borderwidth=2)
container.pack_propagate(False)
container.pack(side=tk.TOP, anchor=tk.N, padx=5, pady=5)

title_label = tk.Label(container, text="Title")
title_label.pack(side=tk.TOP, anchor=tk.N, padx=5, pady=0)

add_button = tk.Button(container, text="New", bg=button_color, command=add_element_clicked)
add_button.pack(side=tk.TOP, anchor=tk.N, padx=5, pady=(0, 5), fill=tk.X)

# Start the main event loop
app.mainloop()
