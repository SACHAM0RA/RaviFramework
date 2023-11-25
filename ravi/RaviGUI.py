import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from ravi.Ravi import *


def rgb_color(r: int, g: int, b: int):
    return "#%02x%02x%02x" % (r, g, b)


add_button_color = rgb_color(200, 200, 200)

remove_button_color = rgb_color(200, 0, 0)


def indentMultilineString(input_str: str) -> str:
    return '\n'.join(['\t' + line for line in input_str.splitlines()])


##############################################################
####################### WIDGET CLASSES #######################
##############################################################

class WidgetElement(object):
    def __init__(self, owner, masterWidget):
        self.owner = owner
        self.masterWidget = masterWidget
        self.widget = self.generateWidget()

    # for implementation by children
    def generateWidget(self):
        return None

    # for implementation by children
    def generateCode(self, globals_list) -> str:
        return "NO CODE"

    def exportDataDictionary(self):
        pass

    def importDataDictionary(self, data):
        pass


class NamedCodeElement(WidgetElement):
    def __init__(self, owner, masterWidget, nameTitle="Name", bodyTitle="Body", bodyHeight=4, bodyWidth=40):
        self.nameTitle = nameTitle
        self.bodyTitle = bodyTitle
        self.bodyHeight = bodyHeight
        self.bodyWidth = bodyWidth
        WidgetElement.__init__(self, owner, masterWidget)

    def generateWidget(self):
        container = tk.Frame(self.masterWidget, relief=tk.GROOVE, borderwidth=2)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_container = tk.Frame(container)
        input_container.pack(anchor=tk.NW, side=tk.LEFT)

        name_container = tk.Frame(input_container)
        name_container.pack(expand=True, fill=tk.BOTH)

        name_label = tk.Label(name_container, text=self.nameTitle)
        name_label.pack(side=tk.LEFT)

        self.name_entry = tk.Entry(name_container, font=("Consolas", 10))
        self.name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        imp_container = tk.Frame(input_container)
        imp_container.pack(expand=True, fill=tk.BOTH)

        imp_label = tk.Label(imp_container, text=self.bodyTitle)
        imp_label.pack(side=tk.TOP, anchor=tk.NW)

        # Create a vertical scrollbar
        vsb = tk.Scrollbar(imp_container, orient="vertical")
        vsb.pack(side="right", fill="y")

        # Create a horizontal scrollbar
        hsb = tk.Scrollbar(imp_container, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        self.imp_text = tk.Text(imp_container, font=("Consolas", 10), height=self.bodyHeight, width=self.bodyWidth,
                                wrap="none", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.imp_text.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # Link the scrollbars to the text widget
        vsb.config(command=self.imp_text.yview)
        hsb.config(command=self.imp_text.xview)

        button_container = tk.Frame(container)
        button_container.pack(fill=tk.Y, expand=True, padx=(2, 0))

        remove_button = tk.Button(button_container,
                                  text=" ",
                                  bg=remove_button_color,
                                  command=lambda: self.owner.remove_element_clicked(self))
        remove_button.pack(expand=True, fill=tk.BOTH)

        return container

    def exportDataDictionary(self):
        data = {
            "name": self.name_entry.get(),
            "imp": self.imp_text.get("1.0", "end-1c")
        }
        return data

    def importDataDictionary(self, data):
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data["name"])

        self.imp_text.delete(1.0, tk.END)
        self.imp_text.insert(tk.END, data["imp"])


class ValueSetElement(NamedCodeElement):
    def __init__(self, owner, masterWidget, nameTitle, bodyTitle, bodyHeight, bodyWidth):
        NamedCodeElement.__init__(self, owner, masterWidget, "Set Name", "Members", 4, 40)

    def generateCode(self, globals_list) -> str:
        header = "class " + self.name_entry.get() + "(Enum):" + '\n'

        bodyText = self.imp_text.get("1.0", "end-1c")

        lines = bodyText.split('\n')
        bodyText = ""
        for index in range(0, len(lines)):
            bodyText = bodyText + '\t' + lines[index] + "=" + str(index + 1) + '\n'

        return header + bodyText + '\n'


class FilterElement(NamedCodeElement):
    def __init__(self, owner, masterWidget, nameTitle, bodyTitle, bodyHeight, bodyWidth):
        NamedCodeElement.__init__(self, owner, masterWidget, "Filter Name", "Specification", 4, 45)

    def generateCode(self, globals_list) -> str:
        global global_list
        header = "def " + self.name_entry.get() + "(s: NarrativeState) -> bool:" + '\n' + '\n'
        for g in globals_list:
            header = header + '\t' + "global " + g + '\n'
        bodyText = '\n' + '\t' + "return " + self.imp_text.get("1.0", "end-1c") + '\n'
        return header + bodyText + '\n'


class TransformElement(NamedCodeElement):
    def __init__(self, owner, masterWidget, nameTitle, bodyTitle, bodyHeight, bodyWidth):
        NamedCodeElement.__init__(self, owner, masterWidget, "Transform Name", "Specification", 4, 45)

    def generateCode(self, globals_list) -> str:
        header = "def " + self.name_entry.get() + "(s: NarrativeState) -> NarrativeState:" + '\n' + '\n'
        for g in globals_list:
            header = header + '\t' + "global " + g + '\n'
        imp_code = indentMultilineString(self.imp_text.get("1.0", "end-1c"))
        bodyText = '\n' + imp_code + '\n' + '\t' + "return s" + '\n'
        return header + bodyText + '\n'


class SingleElement(WidgetElement):
    def __init__(self, owner, masterWidget):
        WidgetElement.__init__(self, owner, masterWidget)

    def generateWidget(self):
        container = tk.Frame(self.masterWidget, relief=tk.GROOVE, borderwidth=2)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_container = tk.Frame(container)
        input_container.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        entry_container = tk.Frame(input_container)
        entry_container.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.value_entry = tk.Entry(entry_container, font=("Consolas", 10))
        self.value_entry.pack(side=tk.TOP, expand=True, fill=tk.X)

        button_container = tk.Frame(container)
        button_container.pack(fill=tk.Y, expand=True, padx=(2, 0))

        remove_button = tk.Button(button_container,
                                  text=" ",
                                  bg=remove_button_color,
                                  command=lambda: self.owner.remove_element_clicked(self))
        remove_button.pack(expand=True, fill=tk.BOTH)

        return container

    def generateCode(self, globals_list) -> str:
        return self.value_entry.get() + '\n'

    def exportDataDictionary(self):
        data = {
            "value": self.value_entry.get()
        }
        return data

    def importDataDictionary(self, data):
        self.value_entry.delete(0, tk.END)
        self.value_entry.insert(0, data["value"])


class ClassElement(WidgetElement):
    def __init__(self, owner, masterWidget, nameTitle="Name", bodyTitle="Body", bodyHeight=3, bodyWidth=40,
                 parentTitle="parent"):
        self.nameTitle = nameTitle
        self.bodyTitle = bodyTitle
        self.bodyHeight = bodyHeight
        self.bodyWidth = bodyWidth
        self.parentTitle = parentTitle
        WidgetElement.__init__(self, owner, masterWidget)

    def generateWidget(self):
        container = tk.Frame(self.masterWidget, relief=tk.GROOVE, borderwidth=2)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_container = tk.Frame(container)
        input_container.pack(anchor=tk.NW, side=tk.LEFT)

        def_container = tk.Frame(input_container)
        def_container.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

        label_container = tk.Frame(def_container)
        label_container.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

        name_label = tk.Label(label_container, text=self.nameTitle)
        name_label.pack(side=tk.TOP, anchor=tk.NW)

        parent_label = tk.Label(label_container, text=self.parentTitle)
        parent_label.pack(side=tk.TOP, anchor=tk.NW)

        entry_container = tk.Frame(def_container)
        entry_container.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

        self.name_entry = tk.Entry(entry_container, font=("Consolas", 10))
        self.name_entry.pack(side=tk.TOP, expand=True, fill=tk.X)

        self.parent_entry = tk.Entry(entry_container, font=("Consolas", 10))
        self.parent_entry.pack(side=tk.TOP, expand=True, fill=tk.X)

        imp_container = tk.Frame(input_container)
        imp_container.pack(expand=True, fill=tk.BOTH)

        imp_label = tk.Label(imp_container, text=self.bodyTitle)
        imp_label.pack(side=tk.TOP, anchor=tk.NW)

        # Create a vertical scrollbar
        vsb = tk.Scrollbar(imp_container, orient="vertical")
        vsb.pack(side="right", fill="y")

        # Create a horizontal scrollbar
        hsb = tk.Scrollbar(imp_container, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        self.imp_text = tk.Text(imp_container, font=("Consolas", 10), height=self.bodyHeight, width=self.bodyWidth,
                                wrap="none", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.imp_text.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # Link the scrollbars to the text widget
        vsb.config(command=self.imp_text.yview)
        hsb.config(command=self.imp_text.xview)

        button_container = tk.Frame(container)
        button_container.pack(fill=tk.Y, expand=True, padx=(2, 0))

        remove_button = tk.Button(button_container,
                                  text=" ",
                                  bg=remove_button_color,
                                  command=lambda: self.owner.remove_element_clicked(self))
        remove_button.pack(expand=True, fill=tk.BOTH)

        return container

    def generateCode(self, globals_list) -> str:
        class_name = self.name_entry.get()
        parent_name = self.parent_entry.get()
        header = ""
        if parent_name.isspace() or parent_name == "":
            header = class_name + "=" + "EntityClass()" + '\n'
        else:
            header = class_name + "=inherit_from(" + parent_name + ")" + '\n'

        bodyText = self.imp_text.get("1.0", "end-1c")

        lines = bodyText.split('\n')
        bodyText = ""
        for line in lines:
            split_res = line.split(":")
            p_name = split_res[0]
            split_res = split_res[1].split("=")
            t_name = split_res[0]
            d_name = split_res[1]
            bodyText = bodyText + class_name + ".addProperty(" + p_name + "," + t_name + "," + d_name + ")" + '\n'

        return header + bodyText

    def exportDataDictionary(self):
        data = {
            "name": self.name_entry.get(),
            "parent": self.parent_entry.get(),
            "imp": self.imp_text.get("1.0", "end-1c")
        }
        return data

    def importDataDictionary(self, data):
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data["name"])

        self.parent_entry.delete(0, tk.END)
        self.parent_entry.insert(0, data["parent"])

        self.imp_text.delete(1.0, tk.END)
        self.imp_text.insert(tk.END, data["imp"])


class PairElement(WidgetElement):
    def __init__(self, owner, masterWidget, nameTitle="Name", bodyTitle="Body"):
        self.nameTitle = nameTitle
        self.bodyTitle = bodyTitle
        WidgetElement.__init__(self, owner, masterWidget)

    def generateWidget(self):
        container = tk.Frame(self.masterWidget, relief=tk.GROOVE, borderwidth=2)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_container = tk.Frame(container)
        input_container.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        label_container = tk.Frame(input_container)
        label_container.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        name_label = tk.Label(label_container, text=self.nameTitle)
        name_label.pack(side=tk.TOP, anchor=tk.NW)

        imp_label = tk.Label(label_container, text=self.bodyTitle)
        imp_label.pack(side=tk.TOP, anchor=tk.NW)

        entry_container = tk.Frame(input_container)
        entry_container.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.name_entry = tk.Entry(entry_container, font=("Consolas", 10))
        self.name_entry.pack(side=tk.TOP, expand=True, fill=tk.X)

        self.value_entry = tk.Entry(entry_container, font=("Consolas", 10))
        self.value_entry.pack(side=tk.TOP, expand=True, fill=tk.X)

        button_container = tk.Frame(container)
        button_container.pack(fill=tk.Y, expand=True, padx=(2, 0))

        remove_button = tk.Button(button_container,
                                  text=" ",
                                  bg=remove_button_color,
                                  command=lambda: self.owner.remove_element_clicked(self))
        remove_button.pack(expand=True, fill=tk.BOTH)

        return container

    def exportDataDictionary(self):
        data = {
            "name": self.name_entry.get(),
            "value": self.value_entry.get()
        }
        return data

    def importDataDictionary(self, data):
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data["name"])

        self.value_entry.delete(0, tk.END)
        self.value_entry.insert(0, data["value"])


class ConstantElement(PairElement):
    def __init__(self, owner, masterWidget, nameTitle, bodyTitle):
        PairElement.__init__(self, owner, masterWidget, "Constant Name", "Constant Value")

    def generateCode(self, globals_list) -> str:
        header = self.name_entry.get() + "="
        value = self.value_entry.get()
        return header + value + '\n'


class ContextEntityElement(PairElement):
    def __init__(self, owner, masterWidget, nameTitle, bodyTitle):
        PairElement.__init__(self, owner, masterWidget, "Entity Name", "Entity Class")

    def generateCode(self, globals_list) -> str:
        # context = NarrativeContext()
        code = "context.addEntity(" + self.name_entry.get() + ',' + self.value_entry.get() + ")" + '\n'
        return code


class ChoiceElement(WidgetElement):
    def __init__(self, owner, masterWidget, bodyHeight=2, bodyWidth=40):
        self.bodyHeight = bodyHeight
        self.bodyWidth = bodyWidth
        WidgetElement.__init__(self, owner, masterWidget)

    def generateWidget(self):
        container = tk.Frame(self.masterWidget, relief=tk.GROOVE, borderwidth=2)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_container = tk.Frame(container)
        input_container.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        def_container = tk.Frame(input_container)
        def_container.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

        label_container = tk.Frame(def_container)
        label_container.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

        name_label = tk.Label(label_container, text="Choice Name")
        name_label.pack(side=tk.TOP, anchor=tk.NW)

        filter_label = tk.Label(label_container, text="Filter")
        filter_label.pack(side=tk.TOP, anchor=tk.NW)

        trans_label = tk.Label(label_container, text="Transform")
        trans_label.pack(side=tk.TOP, anchor=tk.NW)

        imp_label = tk.Label(label_container, text="Friendly Description")
        imp_label.pack(side=tk.TOP, anchor=tk.NW)

        entry_container = tk.Frame(def_container)
        entry_container.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

        self.name_entry = tk.Entry(entry_container, font=("Consolas", 10))
        self.name_entry.pack(side=tk.TOP, expand=True, fill=tk.X)

        self.filter_entry = tk.Entry(entry_container, font=("Consolas", 10))
        self.filter_entry.pack(side=tk.TOP, expand=True, fill=tk.X)

        self.trans_entry = tk.Entry(entry_container, font=("Consolas", 10))
        self.trans_entry.pack(side=tk.TOP, expand=True, fill=tk.X)

        self.friendly_text = tk.Entry(entry_container, font=("Consolas", 10))
        self.friendly_text.pack(side=tk.TOP, expand=True, fill=tk.X)

        button_container = tk.Frame(container)
        button_container.pack(fill=tk.Y, expand=True, padx=(2, 0))

        remove_button = tk.Button(button_container,
                                  text=" ",
                                  bg=remove_button_color,
                                  command=lambda: self.owner.remove_element_clicked(self))
        remove_button.pack(expand=True, fill=tk.BOTH)

        return container

    def generateCode(self, globals_list) -> str:
        choice_name = self.name_entry.get()
        filter_name = self.filter_entry.get()
        trans_name = self.trans_entry.get()
        friendly = self.friendly_text.get()
        if friendly[0] != '"':
            friendly = '"' + friendly + '"'
        return choice_name + "=NarrativeChoice(" + filter_name + "," + trans_name + "," + friendly + ")" + '\n'

    def exportDataDictionary(self):
        data = {
            "name": self.name_entry.get(),
            "filter": self.filter_entry.get(),
            "transform": self.trans_entry.get(),
            "friendlyName": self.friendly_text.get()
        }
        return data

    def importDataDictionary(self, data):
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data["name"])

        self.filter_entry.delete(0, tk.END)
        self.filter_entry.insert(0, data["filter"])

        self.trans_entry.delete(0, tk.END)
        self.trans_entry.insert(0, data["transform"])

        self.friendly_text.delete(0, tk.END)
        self.friendly_text.insert(0, data["friendlyName"])


class QueryElement(WidgetElement):
    def __init__(self, owner, masterWidget, nameTitle="Query Name", bodyTitle="Implementation", bodyHeight=12,
                 bodyWidth=60):
        self.nameTitle = nameTitle
        self.bodyTitle = bodyTitle
        self.bodyHeight = bodyHeight
        self.bodyWidth = bodyWidth
        WidgetElement.__init__(self, owner, masterWidget)

    def generateWidget(self):
        container = tk.Frame(self.masterWidget, relief=tk.GROOVE, borderwidth=2)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        input_container = tk.Frame(container)
        input_container.pack(anchor=tk.NW, side=tk.LEFT)

        name_container = tk.Frame(input_container)
        name_container.pack(expand=True, fill=tk.BOTH)

        name_label = tk.Label(name_container, text=self.nameTitle)
        name_label.pack(side=tk.LEFT)

        self.name_entry = tk.Entry(name_container, font=("Consolas", 10))
        self.name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        imp_container = tk.Frame(input_container)
        imp_container.pack(expand=True, fill=tk.BOTH)

        imp_label = tk.Label(imp_container, text=self.bodyTitle)
        imp_label.pack(side=tk.TOP, anchor=tk.NW)

        # Create a vertical scrollbar
        vsb = tk.Scrollbar(imp_container, orient="vertical")
        vsb.pack(side="right", fill="y")

        # Create a horizontal scrollbar
        hsb = tk.Scrollbar(imp_container, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        self.imp_text = tk.Text(imp_container, font=("Consolas", 10), height=self.bodyHeight, width=self.bodyWidth,
                                wrap="none", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.imp_text.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # Link the scrollbars to the text widget
        vsb.config(command=self.imp_text.yview)
        hsb.config(command=self.imp_text.xview)

        ret_container = tk.Frame(input_container)
        ret_container.pack(expand=True, fill=tk.BOTH)

        ret_label = tk.Label(ret_container, text="return")
        ret_label.pack(side=tk.LEFT)

        self.ret_entry = tk.Entry(ret_container, font=("Consolas", 10))
        self.ret_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        button_container = tk.Frame(container)
        button_container.pack(fill=tk.Y, expand=True, padx=(2, 0))

        remove_button = tk.Button(button_container,
                                  text=" ",
                                  bg=remove_button_color,
                                  command=lambda: self.owner.remove_element_clicked(self))
        remove_button.pack(expand=True, fill=tk.BOTH)

        return container

    def exportDataDictionary(self):
        data = {
            "name": self.name_entry.get(),
            "imp": self.imp_text.get("1.0", "end-1c"),
            "ret": self.ret_entry.get()
        }
        return data

    def importDataDictionary(self, data):
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data["name"])

        self.imp_text.delete(1.0, tk.END)
        self.imp_text.insert(tk.END, data["imp"])

        self.ret_entry.delete(0, tk.END)
        self.ret_entry.insert(0, data["ret"])

    def generateCode(self, globals_list) -> str:
        q_name = self.name_entry.get()
        q_body = self.imp_text.get("1.0", "end-1c")
        bodyLines = q_body.split('\n')
        q_body = ""
        for index, line in enumerate(bodyLines):
            q_body = q_body + '\t' + line + '\n'
        q_ret = '\t' + "return " + self.ret_entry.get()
        code_str = "def " + q_name + "(model: NarrativeModel):" + '\n' + q_body + '\n' + q_ret
        return code_str + '\n' + '\n'

    def getName(self):
        return self.name_entry.get()


class AssertionElement(NamedCodeElement):
    def __init__(self, owner, masterWidget, nameTitle, bodyTitle, bodyHeight, bodyWidth):
        NamedCodeElement.__init__(self, owner, masterWidget, "Description", "Specification", 12, 66)

    def generateCode(self, globals_list) -> str:
        header = "NarrativeAssertion(" + '\n'
        header = header + '"' + self.name_entry.get() + '"' + "," + '\n'
        # for g in globals_list:
        #    header = header + '\t' + "global " + g + '\n'
        header = header + self.imp_text.get("1.0", "end-1c") + '\n'
        return header + ")" + '\n'


############################################################
####################### LIST CLASSES #######################
############################################################

class ElementList(WidgetElement):
    def __init__(self, owner, masterWidget, classType, title: str):
        self.elements = []
        self.classType = classType
        self.title = title
        WidgetElement.__init__(self, owner, masterWidget)

    def generateWidget(self):
        topContainer = tk.Frame(self.masterWidget, relief=tk.GROOVE, borderwidth=2)
        topContainer.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=(25, 5))

        container = tk.Frame(topContainer, width=300, height=50)
        container.pack_propagate(False)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        title_label = tk.Label(container, text=self.title)
        title_label.pack(side=tk.TOP, anchor=tk.N)

        add_button = tk.Button(container, text="New", bg=add_button_color, command=self.add_element_clicked)
        add_button.pack(side=tk.TOP, anchor=tk.N, fill=tk.X)

        return topContainer

    # for implementation by children
    def generateElement(self) -> object:
        return self.classType(self, self.widget)

    def add_element_clicked(self):
        element = self.generateElement()
        self.elements.append(element)

    def remove_element_clicked(self, element):
        self.elements.remove(element)
        element.widget.pack_forget()

    def generateCode(self, globals_list) -> str:
        code = ""
        for element in self.elements:
            code = code + element.generateCode(globals_list)
        return code + '\n'

    def exportDataDictionary(self):
        data = {}
        for index, element in enumerate(self.elements):
            data[index] = element.exportDataDictionary()
        return data

    def importDataDictionary(self, data):
        allElements = self.elements.copy()
        for element in allElements:
            self.remove_element_clicked(element)

        for index, elementData in data.items():
            self.add_element_clicked()
            self.elements[int(index)].importDataDictionary(elementData)


class NamedCodeList(ElementList):
    def __init__(self, owner, masterWidget, classType, title: str, nameTitle="Name", bodyTitle="Body", bodyHeight=4,
                 bodyWidth=40):
        self.elements = []
        self.classType = classType
        self.title = title
        self.nameTitle = nameTitle
        self.bodyTitle = bodyTitle
        self.bodyHeight = bodyHeight
        self.bodyWidth = bodyWidth
        ElementList.__init__(self, owner, masterWidget, classType, title)

    def generateElement(self) -> object:
        return self.classType(self, self.widget, self.nameTitle, self.bodyTitle, self.bodyHeight, self.bodyWidth)


class TerminationList(ElementList):
    def generateCode(self, globals_list) -> str:
        header = "term_conditions={"
        lines = ElementList.generateCode(self, globals_list).split('\n')
        lines = lines[:-2]
        for line in lines:
            header = header + line + ","
        header = header[:-1] + "}"
        return header + '\n' + '\n'

    def getTerminationNames(self):
        return ElementList.generateCode(self, []).split('\n')[:-2]


class ModelChoiceList(ElementList):
    def generateCode(self, globals_list) -> str:
        body = ElementList.generateCode(self, globals_list)
        definition = "choices=["
        lines = body.split('\n')
        lines = lines[:-2]
        for line in lines:
            definition = definition + line + ','
        definition = definition[:-1] + "]"
        return definition + '\n' + '\n'

    def getChoiceNames(self):
        return ElementList.generateCode(self, []).split('\n')[:-2]


class ClassList(ElementList):
    def __init__(self, owner, masterWidget, classType, title: str, nameTitle="Class Name", bodyTitle="Properties",
                 bodyHeight=4, bodyWidth=40, parentTitle="Parent"):
        self.elements = []
        self.classType = classType
        self.title = title
        self.nameTitle = nameTitle
        self.bodyTitle = bodyTitle
        self.bodyHeight = bodyHeight
        self.bodyWidth = bodyWidth
        self.parentTitle = parentTitle
        ElementList.__init__(self, owner, masterWidget, classType, title)

    def generateElement(self) -> object:
        return self.classType(self, self.widget, self.nameTitle, self.bodyTitle, self.bodyHeight, self.bodyWidth,
                              self.parentTitle)


class ChoiceList(ElementList):
    def __init__(self, owner, masterWidget, classType, title: str, bodyHeight=2, bodyWidth=40):
        self.elements = []
        self.classType = classType
        self.title = title
        self.bodyHeight = bodyHeight
        self.bodyWidth = bodyWidth
        ElementList.__init__(self, owner, masterWidget, classType, title)

    def generateElement(self) -> object:
        return self.classType(self, self.widget, self.bodyHeight, self.bodyWidth)

    def generateCode(self, globals_list) -> str:
        body = ElementList.generateCode(self, globals_list)
        return body + '\n'


class PairList(ElementList):
    def __init__(self, owner, masterWidget, classType, title: str, nameTitle="Name", bodyTitle="Body"):
        self.elements = []
        self.classType = classType
        self.title = title
        self.nameTitle = nameTitle
        self.bodyTitle = bodyTitle
        ElementList.__init__(self, owner, masterWidget, classType, title)

    def generateElement(self) -> object:
        return self.classType(self, self.widget, self.nameTitle, self.bodyTitle)


class ContextEntityList(PairList):
    def generateCode(self, globals_list) -> str:
        header = "context = NarrativeContext()" + '\n'
        return header + PairList.generateCode(self, globals_list) + '\n'


class AssertionsList(NamedCodeList):
    def generateCode(self, globals_list) -> str:
        code_str = ""
        assertion_names = []
        for index, element in enumerate(self.elements):
            name = "assertion_" + str(index)
            assertion_names.append(name)
            assertion = name + "=" + element.generateCode(globals_list) + '\n' + '\n'
            code_str = code_str + assertion

        code_str = '\n' + code_str + "assertions = ["
        for name in assertion_names:
            code_str = code_str + name + ","
        code_str = code_str[:-1] + "]" + '\n'
        return code_str


class QueryList(ElementList):
    def __init__(self, owner, masterWidget, classType, title: str):
        self.elements = []
        self.classType = classType
        self.title = title
        ElementList.__init__(self, owner, masterWidget, classType, title)

    def generateElement(self) -> object:
        return self.classType(self, self.widget)

    def generateCode(self, globals_list) -> str:
        code_str = ""
        for element in self.elements:
            query_def = element.generateCode(globals_list)
            query_name = element.getName()
            query_assign = "self." + query_name + "_VAR=" + query_name + "(self.model)"
            code_str = code_str + query_def + '\n' + query_assign + '\n' + '\n'
        return code_str

    def getVariableNames(self):
        names = []
        for element in self.elements:
            query_name = element.getName()
            names.append("self." + query_name + "_VAR")
        return names

    def getQueryNames(self):
        names = []
        for element in self.elements:
            names.append(element.getName())
        return names


# main application
class appElement(WidgetElement):
    def __init__(self):
        WidgetElement.__init__(self, None, None)

        self.play_visited_states = []
        self.current_play_state = None
        self.model = None
        menu_bar = tk.Menu(self.widget)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open File", command=self.load_data)
        file_menu.add_command(label="Save As", command=self.save_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.widget.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        style = ttk.Style()
        style.configure("TNotebook", padding=(10, 10))
        style.configure("TNotebook.Tab", padding=(10, 5))

        # begin scrollbar

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas = tk.Canvas(self.widget)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.widget, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor=tk.NW)

        frame.bind("<Configure>", on_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        # end scrollbar

        dev_notebook = ttk.Notebook(frame)

        context_tab = tk.Frame(dev_notebook)
        choices_tab = tk.Frame(dev_notebook)
        model_tab = tk.Frame(dev_notebook)
        assertions_tab = tk.Frame(dev_notebook)
        play_tab = tk.Frame(dev_notebook)

        dev_notebook.add(context_tab, text="CONTEXT DEFINITION")
        dev_notebook.add(choices_tab, text="CHOICE DEFINITION")
        dev_notebook.add(model_tab, text="MODEL GENERATION")
        dev_notebook.add(assertions_tab, text="ASSERTION CHECKING")
        dev_notebook.add(play_tab, text="PLAY TESTING")

        ################### BEGIN: CONTEXT TAB ###############


        self.constant_list = PairList(self, context_tab, ConstantElement, "CONSTANTS")
        #self.value_set_list = NamedCodeList(self, context_tab, ValueSetElement, "VALUE SETS")
        self.class_list = ClassList(self, context_tab, ClassElement, "CLASSES")
        self.context_list = ContextEntityList(self, context_tab, ContextEntityElement, "CONTEXT ENTITIES")

        #################### END: CONTEXT TAB ################
        ################### BEGIN: CHOICE TAB ################

        self.filter_list = NamedCodeList(self, choices_tab, FilterElement, "FILTERS")
        self.transform_list = NamedCodeList(self, choices_tab, TransformElement, "TRANSFORMS")
        self.choice_def_list = ChoiceList(self, choices_tab, ChoiceElement, "CHOICES DEFINITIONS")

        ################### END: CHOICE TAB ##################
        ################## BEGIN: MODEL TAB ##################

        self.choice_list = ModelChoiceList(self, model_tab, SingleElement, "MODEL CHOICES")
        self.term_list = TerminationList(self, model_tab, SingleElement, "MODEL TERMINATION")

        self.model_frame = tk.Frame(model_tab, relief=tk.GROOVE, borderwidth=2)
        self.model_frame.pack(anchor=tk.N, side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=(25, 5))

        title_label = tk.Label(self.model_frame, text="MODEL GENERATION AND VISUALIZATION")
        title_label.pack(fill=tk.X, pady=(5, 0))

        generate_button = tk.Button(self.model_frame,
                                    text="GENERATE MODEL",
                                    bg=add_button_color,
                                    command=lambda: self.executeModelGenerationCode())
        generate_button.pack(fill=tk.X, padx=5, pady=(0, 8))

        self.show_choice_var = tk.IntVar()
        show_choice_checkbox = tk.Checkbutton(self.model_frame, text="Show Choices", variable=self.show_choice_var)
        show_choice_checkbox.pack(anchor=tk.W)

        self.rot_choice_var = tk.IntVar()
        rot_choice_checkbox = tk.Checkbutton(self.model_frame, text="Rotate Choices", variable=self.rot_choice_var)
        rot_choice_checkbox.pack(anchor=tk.W)

        ##################### END: MODEL TAB #####################
        ################## BEGIN: ASSERTION TAB ##################

        self.query_list = QueryList(self, assertions_tab, QueryElement, "QUERIES")
        self.assertion_list = AssertionsList(self, assertions_tab, AssertionElement, "ASSERTIONS")

        self.result_frame = tk.Frame(assertions_tab, relief=tk.GROOVE, borderwidth=2)
        self.result_frame.pack(anchor=tk.N, side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=(25, 5))

        title_label = tk.Label(self.result_frame, text="ASSERTIONS AND QUERY RESULTS")
        title_label.pack(fill=tk.X, pady=(5, 0))

        result_button = tk.Button(self.result_frame,
                                  text="CHECK ASSERTIONS",
                                  bg=add_button_color,
                                  command=lambda: self.executeAssertionCheckingCode())
        result_button.pack(fill=tk.X, padx=5, pady=(0, 8))

        ################## END: ASSERTION TAB ####################
        #################### BEGIN: PLAY TAB #####################

        result_button = tk.Button(play_tab,
                                  text="START",
                                  bg=add_button_color,
                                  command=lambda: self.start_play(), padx=15)
        result_button.pack(anchor=tk.W, side=tk.TOP, padx=50, pady=(50, 5))

        self.options_frame = tk.Frame(play_tab, relief=tk.GROOVE, borderwidth=2)
        self.options_frame.pack(anchor=tk.N, side=tk.LEFT, padx=(50, 5), pady=(5, 5))

        self.options_label = tk.Label(self.options_frame, text="CURRENT OPTIONS")
        self.options_label.pack(pady=10)

        self.states_frame = tk.Frame(play_tab, relief=tk.GROOVE, borderwidth=2)
        self.states_frame.pack(anchor=tk.N, side=tk.LEFT, padx=(5, 50), pady=(5, 5))

        self.play_states_label = tk.Label(self.states_frame, text="PROGRESS ON MODEL")
        self.play_states_label.pack(pady=10)

        ##################### END: PLAY TAB ######################

        dev_notebook.pack(fill=tk.BOTH, expand=True)

        self.widget.config(menu=menu_bar)
        self.widget.mainloop()

    def save_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w') as json_file:
                data = self.exportDataDictionary()
                json.dump(data, json_file, indent=4)

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                self.importDataDictionary(data)

    def generateWidget(self):
        app = tk.Tk()
        app.title("RAVI GUI")

        app.minsize(1730, 910)

        return app

    def generateCode(self, globals_list) -> str:
        code = ""
        code = code + "from enum import *" + '\n'
        code = code + "from ravi.Ravi import *" + '\n' + '\n'
        code = code + self.constant_list.generateCode(globals_list)
        #code = code + self.value_set_list.generateCode(globals_list)
        code = code + self.class_list.generateCode(globals_list)
        code = code + self.context_list.generateCode(globals_list)
        code = code + self.filter_list.generateCode(globals_list)
        code = code + self.transform_list.generateCode(globals_list)
        code = code + self.choice_def_list.generateCode(globals_list)
        code = code + self.term_list.generateCode(globals_list)
        code = code + self.choice_list.generateCode(globals_list)

        code = code + "initial_states = {NarrativeState(context)}" + '\n'
        code = code + "settings: NarrationSetting = NarrationSetting(initial_states=initial_states, termination_conditions=term_conditions, choices=choices)" + '\n'
        code = code + "self.model: NarrativeModel = generateNarrativeModel(setting=settings, max_depth=math.inf)" + '\n'
        # code = code + "model.runNarration(False, NarrativeState(context))" + '\n'

        code = code + "self.model.drawNarrationGraph(show_state=False, show_choices={}, show_plot=False, rotate_labels={})".format(
            self.show_choice_var.get(), self.rot_choice_var.get())

        return code

    def getModelGenerationCode(self) -> str:
        globals_list = []
        constants = self.constant_list.generateCode(globals_list).split('\n')
        for c in constants:
            if not c.isspace() and c != "":
                globals_list.append(c.split("=")[0])

        choices_name = self.choice_list.getChoiceNames()
        for ch_name in choices_name:
            if not ch_name.isspace() and ch_name != "":
                globals_list.append(ch_name)

        term_names = self.term_list.getTerminationNames()
        for t_name in term_names:
            if not t_name.isspace() and t_name != "":
                globals_list.append(t_name)

        q_names = self.query_list.getQueryNames()
        for q_name in q_names:
            if not q_name.isspace() and q_name != "":
                globals_list.append(q_name)

        code_str = self.generateCode(globals_list)
        return code_str

    def executeModelGenerationCode(self):
        plt.clf()

        code_str = self.getModelGenerationCode()
        print(code_str)
        exec(code_str)

        try:
            self.model_preview_frame.pack_forget()
        except:
            pass

        self.model_preview_frame = tk.Frame(self.model_frame, relief=tk.GROOVE, borderwidth=2)
        self.model_preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        self.preview_canvas = FigureCanvasTkAgg(plt.gcf(), master=self.model_preview_frame)
        self.preview_canvas.draw()
        self.preview_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def executeAssertionCheckingCode(self):
        code_str = self.getModelGenerationCode() + '\n'

        query_section = self.query_list.generateCode([]) + '\n' + '\n'

        assertion_definitions = self.assertion_list.generateCode([]) + '\n'
        self.assertion_results = []
        assertion_execution = "self.assertion_results = self.model.validateAssertions(assertions=assertions, print_results=False)"
        assertion_section = assertion_definitions + assertion_execution

        code_str = code_str + query_section + assertion_section
        print(code_str)
        exec(code_str)

        try:
            self.query_results_label.pack_forget()
            self.assertion_results_label.pack_forget()
        except:
            pass

        self.query_results = []
        var_names = self.query_list.getVariableNames()
        for var in var_names:
            nice_name = var[5:-4]
            self.query_results.append(nice_name + " = " + str(eval(var)))

        if len(self.query_results) != 0:
            self.query_results_label = tk.Text(self.result_frame, wrap=tk.WORD, width=40,
                                               background="black", font=("Consolas", 9, "bold"), padx=5, pady=5)
            self.query_results_label.tag_config("white", foreground=rgb_color(255, 255, 255))
            for r in self.query_results:
                self.query_results_label.insert(tk.END, r + '\n', "white")
            self.query_results_label.pack(padx=5, pady=(5, 5), expand=True, fill=tk.X)

        line_num = (len(self.assertion_results))*2
        self.assertion_results_label = tk.Text(self.result_frame, wrap=tk.WORD, width=40,
                                               background="black", font=("Consolas", 9, "bold"), padx=5, pady=5)
        self.assertion_results_label.tag_config("pass", foreground=rgb_color(0, 255, 0))
        self.assertion_results_label.tag_config("fail", foreground=rgb_color(255, 0, 0))
        for r in self.assertion_results:
            stype = "pass"
            if (r[-1] == "L"):
                stype = "fail"
            self.assertion_results_label.insert(tk.END, r + '\n' + '\n', stype)
        self.assertion_results_label.pack(padx=5, pady=(5, 5), expand=True, fill=tk.X)

    def start_play(self):
        self.executeModelGenerationCode()
        self.play_visited_states.clear()
        self.current_play_state = list(self.model.initialStates)[0]
        self.show_choice_buttons()

    def shouldContinuePlay(self):
        return len(getPossibleChoices(self.current_play_state, self.model.choices)) > 0 and \
               not (self.current_play_state in self.model.terminationStates)

    def show_choice_buttons(self):
        self.play_visited_states.append(self.current_play_state)

        try:
            self.play_preview_frame.pack_forget()
        except:
            pass

        self.play_preview_frame = tk.Frame(self.states_frame)
        self.play_preview_frame.pack(padx=5, pady=(0, 5))

        plt.clf()
        self.model.drawNarrationGraphWithHighlights(show_state=False,
                                                    show_choices=True,
                                                    show_plot=False,
                                                    rotate_labels=False,
                                                    highlight_states=self.play_visited_states)

        self.play_canvas = FigureCanvasTkAgg(plt.gcf(), master=self.play_preview_frame)
        self.play_canvas.draw()
        self.play_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        if not self.shouldContinuePlay():

            try:
                self.term_label.pack_forget()
            except:
                pass

            self.term_label = tk.Label(self.options_frame, text="NARRATIVE TERMINATED", foreground="red",
                                       font=("Consolas", 10, "bold italic"))
            self.term_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 5))
            return

        for child in self.options_frame.winfo_children():
            if child != self.options_label:
                child.pack_forget()

        possible_choices = getPossibleChoices(self.current_play_state, self.model.choices)
        for index, choice in possible_choices.items():
            option_btn = tk.Button(self.options_frame,
                                   text="[" + str(index) + "] : " + str(choice),
                                   bg=add_button_color,
                                   font=("Consolas", 10, "bold italic"),
                                   width=60,
                                   command=lambda id=index: self.on_play_choice_clicked(id))
            option_btn.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(0, 5))

    def on_play_choice_clicked(self, option_index):

        if not self.shouldContinuePlay():
            return

        possible_choices = getPossibleChoices(self.current_play_state, self.model.choices)
        self.current_play_state = possible_choices[option_index].Action(self.current_play_state)
        self.show_choice_buttons()

    def exportDataDictionary(self):
        data = {
            "constants": self.constant_list.exportDataDictionary(),
            #"value_sets": self.value_set_list.exportDataDictionary(),
            "classes": self.class_list.exportDataDictionary(),
            "context_entities": self.context_list.exportDataDictionary(),
            "filters": self.filter_list.exportDataDictionary(),
            "transforms": self.transform_list.exportDataDictionary(),
            "choice_def": self.choice_def_list.exportDataDictionary(),
            "terminations": self.term_list.exportDataDictionary(),
            "model_choices": self.choice_list.exportDataDictionary(),
            "assertions": self.assertion_list.exportDataDictionary(),
            "queries": self.query_list.exportDataDictionary(),
        }
        return data

    def importDataDictionary(self, data):
        self.constant_list.importDataDictionary(data["constants"])
        #self.value_set_list.importDataDictionary(data["value_sets"])
        self.class_list.importDataDictionary(data["classes"])
        self.context_list.importDataDictionary(data["context_entities"])
        self.filter_list.importDataDictionary(data["filters"])
        self.transform_list.importDataDictionary(data["transforms"])
        self.choice_def_list.importDataDictionary(data["choice_def"])
        self.term_list.importDataDictionary(data["terminations"])
        self.choice_list.importDataDictionary(data["model_choices"])
        self.assertion_list.importDataDictionary(data["assertions"])
        self.query_list.importDataDictionary(data["queries"])


application = appElement()
