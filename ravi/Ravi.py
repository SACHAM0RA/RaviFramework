import math
import string
import textwrap
from types import FunctionType
from copy import copy, deepcopy
import inspect
from typing import List, Dict, Set
import networkx as nx
import matplotlib.pyplot as plt

NULL_STRING: string = "NULL"
CLASS_TYPE: string = "class_type"
DEFAULT_VALUE: string = "default_value"


# =========================================================== Sets =====================================================


class StateSet(set):
    def __init__(self, *args):
        set.__init__(self, *args)

    def __str__(self):
        ret = ""
        for state in self:
            ret = ret + str(state) + '\n' + "###########################################" + '\n'
        return ret


class ChoiceSet(set):
    def __init__(self, *args):
        set.__init__(self, *args)

    def __str__(self):
        ret = "\n"
        for state in self:
            ret = ret + '-- ' + str(state) + '\n'
        return ret


class EventSet(set):
    def __init__(self, *args):
        set.__init__(self, *args)

    def __str__(self):
        ret = ""
        for state in self:
            ret = ret + str(state) + '\n' + "###########################################" + '\n'
        return ret


class PathSet(set):
    def __init__(self, *args):
        set.__init__(self, *args)

    def __str__(self):
        ret = ""
        for path in self:
            ret = ret + str(path) + '\n' + "###########################################" + '\n'
        return ret


# ===================================================== EntityClass =================================================


class EntityClass(object):
    def __init__(self):
        self._properties = dict()

    def __repr__(self):
        return repr(self._properties)

    def __str__(self):
        return str(self._properties)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self._properties)

    def __copy__(self):
        new = EntityClass()
        new._properties = deepcopy(self._properties)
        return new

    def __deepcopy__(self, memo):
        return copy(self)

    def addProperty(self, property_name: string, class_type, default_value):
        self._properties[property_name] = {CLASS_TYPE: class_type, DEFAULT_VALUE: default_value}

    def removeProperty(self, property_name: string):
        del self._properties[property_name]

    def changePropertyDefaultValue(self, property_name: string, new_default_value):
        self._properties[property_name][DEFAULT_VALUE] = new_default_value

    @property
    def properties(self):
        return copy(self._properties)


def inherit_from(parent: EntityClass) -> EntityClass:
    return deepcopy(parent)


# ===================================================== Narrative Context ==============================================

class NarrativeContext(object):
    def __init__(self):
        self._entities = dict()

    def __repr__(self):
        return str(self)

    def __str__(self):
        s: string = "\n"
        for e in self._entities.items():
            s = s + str(e[0]) + "\n" + str(e[1]) + "\n"
        return s

    def __hash__(self):
        h = 0
        for entity in self._entities:
            h += hash(entity)
        return h

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __copy__(self):
        new = NarrativeContext()
        new._entities = deepcopy(self._entities)
        return new

    def __deepcopy__(self, memo):
        return copy(self)

    def addEntity(self, entity_name: string, e_class: EntityClass):
        entityT = deepcopy(e_class)
        self._entities[entity_name] = entityT

    def setDefaultValue(self, entity_name: string, property_name: string, default_value):
        self._entities[entity_name].changePropertyDefaultValue(property_name, default_value)

    def removeEntity(self, name: string):
        del self._entities[name]

    def doesHaveEntity(self, entity_name: string):
        return list(self._entities.keys()).count(entity_name) == 1

    @property
    def entities(self):
        return deepcopy(self._entities)


# ===================================================== Entity Instance ================================================

class Entity(object):
    def __init__(self, e_class: EntityClass):
        self._entityClass: EntityClass = deepcopy(e_class)
        self._valuation = dict()
        for pair in self._entityClass.properties.items():
            property_name = pair[0]
            property_class_type = pair[1][CLASS_TYPE]
            property_default_value = pair[1][DEFAULT_VALUE]
            self._valuation[property_name] = property_class_type(property_default_value)

    def __repr__(self):
        return repr(self._valuation)

    def __str__(self):
        s = ""
        for v in self._valuation.items():
            s = s + "    |---- " + str(v[0]) + " = " + str(v[1]) + "\n"
        return s

    def __hash__(self):
        return hash(self._valuation)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __copy__(self):
        new = Entity(self._entityClass)
        new._valuation = deepcopy(self._valuation)
        return new

    def __deepcopy__(self, memo):
        return copy(self)

    def doesHaveProperty(self, property_name: string):
        return list(self._valuation.keys()).count(property_name) == 1

    def setPropertyValue(self, property_name: string, property_value):

        if self.doesHaveProperty(property_name):
            property_class_type = self._entityClass.properties[property_name][CLASS_TYPE]
            if property_class_type == type(property_value):
                self._valuation[property_name] = property_class_type(property_value)
            else:
                raise TypeError("<" + property_name + "> must be of type " + repr(property_class_type))
        else:
            raise Exception("Cannot find property with the name <" + property_name + ">")

    def getPropertyValue(self, property_name: string):
        if self.doesHaveProperty(property_name):
            return self._valuation[property_name]
        else:
            raise Exception("There is no property named <" + property_name + ">")


# ================================================== Narrative World State =============================================

class NarrativeState(object):
    def __init__(self, context: NarrativeContext):
        self._context = deepcopy(context)
        self._entities = dict()
        for pair in self._context.entities.items():
            self._entities[pair[0]] = Entity(pair[1])

    def __repr__(self):
        return str(self)

    def __str__(self):
        s: string = "\n"
        for e in self._entities.items():
            s = s + str(e[0]) + "\n" + str(e[1])
        return s

    def __hash__(self):
        h = 0
        for entity in self._entities:
            h += hash(entity)
        return h

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __copy__(self):
        newWorldState = NarrativeState(self._context)
        newWorldState._entities = deepcopy(self._entities)
        return newWorldState

    def __deepcopy__(self, memo):
        return copy(self)

    def doesHaveEntity(self, entity_name: string):
        return list(self._entities.keys()).count(entity_name) == 1

    def setValue(self, entity_name: string, property_name: string, value):
        if self.doesHaveEntity(entity_name):
            self._entities[entity_name].setPropertyValue(property_name, value)
        else:
            raise Exception("Cannot find entity with the name <" + entity_name + ">")

    def getValue(self, entity_name: string, property_name: string):
        if self.doesHaveEntity(entity_name):
            return self._entities[entity_name].getPropertyValue(property_name)
        else:
            raise Exception("Cannot find entity with the name <" + entity_name + ">")


# ===================================================== NarrativeChoice ================================================

class NarrativeChoice(object):
    def __init__(self, pre_condition: FunctionType, action: FunctionType, friendly_name: string = ""):
        self._friendlyName = friendly_name

        self._pre_condition: FunctionType = pre_condition

        self._action: FunctionType
        return_type = list(inspect.getfullargspec(action)[6].values())[0]
        first_arg_type = list(inspect.getfullargspec(action)[6].values())[1]
        param_len = len(list(inspect.getfullargspec(action)[6].values()))
        if return_type == NarrativeState and first_arg_type == NarrativeState and param_len == 2:
            self._action = action
        else:
            raise TypeError("Invalid action function signature")

    def __str__(self):
        return self._friendlyName

    def __repr__(self):
        return self._friendlyName

    def __hash__(self):
        return hash(self._friendlyName) + hash(self._pre_condition) + hash(self._action)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def PreCondition(self, w: NarrativeState) -> bool:
        return self._pre_condition(copy(w))

    def Action(self, w: NarrativeState) -> NarrativeState:
        return self._action(copy(w))


# ====================================================== NarrativeEvent ================================================


class NarrativeEvent(object):
    def __init__(self, pre_state: NarrativeState, post_state: NarrativeState, choice: NarrativeChoice):
        self._pre_state = pre_state
        self._post_state = post_state
        self._choice = choice

    def __str__(self):
        return '\n' + "--FROM--" + \
               textwrap.indent(str(self._pre_state), "    ") + '\n' + \
               "--TO--" + \
               textwrap.indent(str(self._post_state), "    ") + '\n' + \
               "--BY--" + '\n' + \
               textwrap.indent(str(self._choice), "    ") + '\n'

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self._pre_state) + hash(self._post_state) + hash(self._choice)

    def __eq__(self, other):
        if not isinstance(other, NarrativeEvent):
            return False

        return self._pre_state == other._pre_state and \
               self._post_state == other._post_state and \
               self._choice == other._choice

    @property
    def Choice(self):
        return deepcopy(self._choice)

    @property
    def PreState(self):
        return deepcopy(self._pre_state)

    @property
    def PostState(self):
        return deepcopy(self._post_state)


# ======================================================= NarrativePath ================================================


class NarrativePath(object):
    def __init__(self, stateList: List[NarrativeState], choiceList: List[NarrativeChoice]):
        self._states: List[NarrativeState] = stateList
        self._choices: List[NarrativeChoice] = choiceList

    def __str__(self):
        ret: string = str(self._states[0])
        for i in range(1, len(self._states)):
            ret = ret + " -> " + " BY " + str(self._choices[i - 1]) + " TO " + str(self._states[i])
        return ret

    def __repr__(self):
        return str(self)

    def __hash__(self):
        ret = 0

        for state in self._states:
            ret = ret + hash(state)

        for choice in self._choices:
            ret = ret + hash(choice)

        return ret

    def __eq__(self, other):
        if isinstance(other, NarrativePath):
            return self._states == other._states and self._choices == other._choices
        return False

    @property
    def States(self):
        return EventSet(deepcopy(self._states))

    @property
    def Choices(self):
        return ChoiceSet(deepcopy(self._choices))

    @property
    def Events(self):
        ret = EventSet()
        for i in range(len(self._states) - 1):
            ret.add(NarrativeEvent(self._states[i], self._states[i + 1], self._choices[i]))
        return ret


# ======================================================== Assertion ===================================================

class NarrativeAssertion(object):
    def __init__(self,
                 friendly_name: string,
                 assertion_func: FunctionType):
        self.friendlyName = friendly_name
        self.assertionFunc = assertion_func


# ======================================================== Narration ===================================================


class NarrationSetting(object):
    def __init__(self,
                 initial_states: Set[NarrativeState],
                 choices: Set[NarrativeChoice],
                 termination_conditions: Set[FunctionType]):
        self.initialStates: Set[NarrativeState] = initial_states
        self.choices: Set[NarrativeChoice] = choices
        self.terminationConditions: Set[FunctionType] = termination_conditions

    def __str__(self):
        return "[" + str(self.initialStates) + "," + str(self.choices) + "," + str(self.terminationConditions) + "]"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.initialStates) + hash(self.choices) + hash(self.terminationConditions)

    def __eq__(self, other):
        if not isinstance(other, NarrationSetting):
            return False
        else:
            return self.initialStates == other.initialStates and \
                   self.choices == other.choices and \
                   self.terminationConditions == other.terminationConditions


class NarrativeModel(object):
    def __init__(self,
                 initial_states: Set[NarrativeState],
                 termination_states: Set[NarrativeState],
                 termination_conditions: Set[FunctionType],
                 choices: Set[NarrativeChoice],
                 event_set: EventSet,
                 narrative_graph: nx.DiGraph):

        self._initialWorldStates: Set[NarrativeState] = set(deepcopy(initial_states))
        self._terminationStates: Set[NarrativeState] = set(deepcopy(termination_states))
        self._choices: Set[NarrativeChoice] = choices
        self._narrativeGraph: nx.DiGraph = narrative_graph
        self._dead_ends: Set[NarrativeState] = self._findDeadEnds()
        self._terminationConditions: Set[FunctionType] = termination_conditions
        self._eventSet: EventSet = event_set

    def __hash__(self):
        return hash(self._initialWorldStates) + \
               hash(self._terminationStates) + \
               hash(self._choices) + \
               hash(self._narrativeGraph)

    def __eq__(self, other):
        if not isinstance(other, NarrativeModel):
            return False
        else:
            return self._initialWorldStates == other._initialWorldStates and \
                   self._terminationStates == other._terminationStates and \
                   self._choices == other._choices and \
                   self._narrativeGraph == other._narrativeGraph

    def _findDeadEnds(self) -> Set[NarrativeState]:
        dead_ends: Set[NarrativeState] = StateSet()
        for state in list(self._narrativeGraph.nodes):
            if self._narrativeGraph.out_degree[state] == 0 and not (state in self._terminationStates):
                dead_ends.add(state)
        return dead_ends

    def runNarration(self, show_state: bool, initial_world_state: NarrativeState):
        current_state: NarrativeState = deepcopy(initial_world_state)
        choices = self._choices
        print("")
        print("--- Begin: Running Interactive Narration ---")
        if show_state:
            print(initial_world_state)
        while len(getPossibleChoices(current_state, choices)) > 0 and not (current_state in self._terminationStates):
            current_state = interactiveStep(show_state, current_state, choices)

    def drawNarrationGraph(self, show_state: bool, show_choices: bool, show_plot: bool = True,
                           rotate_labels: bool = False):
        # --------------
        # Draw the graph

        node_size = 50
        alpha = 1
        if show_state:
            node_size = 7000
            alpha = 0.1

        initial_color = (0, 1, 0, alpha)
        termination_color = (1, 0, 0, alpha)
        other_color = (0, 0, 0, alpha)

        colors = list()
        for node in self._narrativeGraph.nodes:
            if node in self._initialWorldStates:
                colors.append(initial_color)
            elif node in self._terminationStates:
                colors.append(termination_color)
            else:
                colors.append(other_color)

        G = self._narrativeGraph
        starts = deepcopy(self._initialWorldStates)
        start_node = starts.pop()
        shortest_paths = nx.single_source_shortest_path_length(G, start_node)

        groups = {}
        for node, distance in shortest_paths.items():
            if distance not in groups:
                groups[distance] = []
            groups[distance].append(node)

        pos = {}
        for i, layer in groups.items():
            for j, node in enumerate(layer):
                pos[node] = (i, (j - len(layer) * 0.5))

        # pos = nx.planar_layout(self._narrativeGraph)
        nx.draw(self._narrativeGraph,
                pos=pos,
                with_labels=show_state,
                font_weight='normal',
                font_size='8',
                font_color=(0, 0, 0, 1),
                node_size=node_size,
                node_color=colors,
                node_shape='o')

        if show_choices:
            edge_labels = {(u, v): d['choices'] for u, v, d in G.edges(data=True)}
            nx.draw_networkx_edge_labels(self._narrativeGraph,
                                         pos=pos,
                                         font_size=8,
                                         font_color='k',
                                         rotate=rotate_labels,
                                         edge_labels=edge_labels)

        if show_plot:
            plt.show()

    def drawNarrationGraphWithHighlights(self, show_state: bool, show_choices: bool, show_plot: bool = True,
                                         rotate_labels: bool = False, highlight_states=None):
        # --------------
        # Draw the graph

        if highlight_states is None:
            highlight_states = []

        node_size = 100

        highlight_color = (1, 0, 0, 1)
        other_color = (0, 0, 0, 0.33)

        colors = list()
        node_sizes = list()
        edge_colors = list()
        for node in self._narrativeGraph.nodes:
            if node in highlight_states:
                colors.append(highlight_color)
                node_sizes.append(node_size * 2)
            else:
                colors.append(other_color)
                node_sizes.append(node_size)

        for edge in self._narrativeGraph.edges:
            if edge[0] in highlight_states and edge[1] in highlight_states:
                edge_colors.append(highlight_color)
            else:
                edge_colors.append(other_color)

        G = self._narrativeGraph
        starts = deepcopy(self._initialWorldStates)
        start_node = starts.pop()
        shortest_paths = nx.single_source_shortest_path_length(G, start_node)

        groups = {}
        for node, distance in shortest_paths.items():
            if distance not in groups:
                groups[distance] = []
            groups[distance].append(node)

        pos = {}
        for i, layer in groups.items():
            for j, node in enumerate(layer):
                pos[node] = (i, (j - len(layer) * 0.5))

        # pos = nx.planar_layout(self._narrativeGraph)
        nx.draw(self._narrativeGraph,
                pos=pos,
                with_labels=show_state,
                font_weight='normal',
                font_size='8',
                font_color=(0, 0, 0, 1),
                node_size=node_sizes,
                node_color=colors,
                node_shape='o',
                edge_color=edge_colors,
                width=3.0)

        if show_choices:
            edge_labels = {(u, v): d['choices'] for u, v, d in G.edges(data=True)}
            nx.draw_networkx_edge_labels(self._narrativeGraph,
                                         pos=pos,
                                         font_size=8,
                                         font_color='k',
                                         rotate=rotate_labels,
                                         edge_labels=edge_labels,
                                         label_pos=0.5)

        if show_plot:
            plt.show()

    def validateAssertions(self, assertions: Set[NarrativeAssertion], print_results: bool = True):
        results = []
        print("=== STARTING ASSERTION CHECKING ===")
        i = 0
        for a in assertions:
            i = i + 1
            if a.assertionFunc(self):
                sat = "PASS"
            else:
                sat = "FAIL"

            result = "[" + str(i) + "] " + a.friendlyName + ": " + sat
            results.append(result)
            if print_results:
                print(result)

        print("=== ASSERTION CHECKING COMPLETED ===")
        return results

    @property
    def narrativeGraph(self):
        return deepcopy(self._narrativeGraph)

    @property
    def initialStates(self):
        return deepcopy(self._initialWorldStates)

    @property
    def terminationStates(self):
        return deepcopy(self._terminationStates)

    @property
    def choices(self) -> Set[NarrativeChoice]:
        return deepcopy(self._choices)

    @property
    def deadEnds(self):
        return deepcopy(self._dead_ends)

    @property
    def terminationConditions(self):
        return self._terminationConditions

    def hasAbsoluteTermination(self):
        for state in self._terminationStates:
            if self._narrativeGraph.out_degree[state] != 0:
                return False
        return True

    @property
    def eventSet(self):
        return self._eventSet

    @property
    def assertions(self):
        return self._assertions


# ======================================================= Generation ===================================================


def getPossibleChoices(w: NarrativeState, choices: Set[NarrativeChoice]) -> Dict[int, NarrativeChoice]:
    choice_indices = dict()
    counter = 0
    for i in range(len(choices)):
        if list(choices)[i].PreCondition(w):
            choice_indices[counter] = list(choices)[i]
            counter += 1
    return choice_indices


def interactiveStep(show_state: bool, current_world: NarrativeState,
                    choices: Set[NarrativeChoice]) -> NarrativeState:
    possible_choices = getPossibleChoices(current_world, choices)
    for pair in possible_choices.items():
        print("[" + str(pair[0]) + "] : " + str(pair[1]))
    option_index = int(input("Choose : "))
    print("---------------------------------")
    new_world = possible_choices[option_index].Action(current_world)
    if show_state:
        print(new_world)
    return new_world


def checkForTermination(state: NarrativeState, term_conditions: Set[FunctionType]) -> bool:
    for condition in term_conditions:
        if condition(state):
            return True
    return False


def simulateFrom(root_world_state: NarrativeState,
                 choices: Set[NarrativeChoice],
                 term_conditions: Set[FunctionType],
                 eventSet: EventSet,
                 graph: nx.DiGraph,
                 current_depth: int,
                 max_depth: int):
    possibleChoices = getPossibleChoices(root_world_state, choices)
    if len(possibleChoices) > 0:
        for ch in possibleChoices.values():
            child_world_state = ch.Action(deepcopy(root_world_state))

            if not graph.has_node(child_world_state):
                graph.add_node(child_world_state)
                if not checkForTermination(child_world_state, term_conditions) and current_depth < max_depth:
                    simulateFrom(child_world_state,
                                 choices,
                                 term_conditions,
                                 eventSet,
                                 graph,
                                 current_depth + 1,
                                 max_depth)

            if not graph.has_edge(root_world_state, child_world_state):
                graph.add_edge(root_world_state, child_world_state)

            try:
                graph[root_world_state][child_world_state]["choices"].add(ch)
            except:
                graph[root_world_state][child_world_state]["choices"]: Set = {ch}

            eventSet.add(NarrativeEvent(root_world_state, child_world_state, ch))


def generateNarrativeModel(setting: NarrationSetting, max_depth: int = math.inf,
                           printProcess: bool = True) -> NarrativeModel:
    if printProcess:
        print("=== MODEL GENERATION STARTED ===")
    narrativeGraph: nx.DiGraph = nx.DiGraph()

    def passesAnyTerminationConditions(state) -> bool:
        for cond in setting.terminationConditions:
            if cond(state):
                return True
        return False

    valid_roots = [root for root in setting.initialStates if not passesAnyTerminationConditions(root)]

    for root in valid_roots:
        root_state = deepcopy(root)
        narrativeGraph.add_node(root_state)

    eventSet: EventSet = EventSet()

    for root in valid_roots:
        root_state = deepcopy(root)
        simulateFrom(root_state,
                     setting.choices,
                     setting.terminationConditions,
                     eventSet,
                     narrativeGraph,
                     1,
                     max_depth)

    terminationStates: Set[NarrativeState] = set()
    for node in narrativeGraph.nodes:
        for condition in setting.terminationConditions:
            if condition(node):
                terminationStates.add(node)

    if printProcess:
        print("=== MODEL GENERATION ENDED ===")

    return NarrativeModel(deepcopy(set(valid_roots)),
                          terminationStates,
                          deepcopy(setting.terminationConditions),
                          deepcopy(setting.choices),
                          eventSet,
                          narrativeGraph)


# ============================================= Narration Processing Functions =========================================

def subModelFrom(states: StateSet, narration: NarrativeModel) -> NarrativeModel:
    choices = deepcopy(narration.choices)
    termination_conditions = deepcopy(narration.terminationConditions)
    return generateNarrativeModel(NarrationSetting(initial_states=states,
                                                   choices=choices,
                                                   termination_conditions=termination_conditions),
                                  math.inf,
                                  False)


def filterStates(filter_func: FunctionType, states: StateSet) -> StateSet:
    filtered_set: Set = StateSet()
    for state in states:
        if filter_func(state):
            filtered_set.add(state)
    return filtered_set


def statesOf(context: object) -> StateSet:
    if isinstance(context, NarrativeModel):
        return StateSet(context.narrativeGraph.nodes)
    elif isinstance(context, StateSet):
        return context
    elif isinstance(context, EventSet):
        to_ret = StateSet()
        for event in context:
            to_ret.add(event.PreState)
            to_ret.add(event.PostState)
        return to_ret
    else:
        return StateSet()


def postStatesOf(event_set: EventSet) -> StateSet:
    to_ret = StateSet()
    for event in event_set:
        to_ret.add(event.PostState)
    return to_ret


def preStatesOf(event_set: EventSet) -> StateSet:
    to_ret = StateSet()
    for event in event_set:
        to_ret.add(event.PreState)
    return to_ret


def choicesOf(context: object) -> ChoiceSet:
    if isinstance(context, EventSet):
        to_ret = ChoiceSet()
        for event in context:
            to_ret.add(event.Choice)
        return to_ret
    elif isinstance(context, NarrativeModel):
        to_ret = ChoiceSet()
        for event in eventsIn(context):
            to_ret.add(event.Choice)
        return to_ret


def eventsIn(narration: NarrativeModel) -> EventSet:
    return deepcopy(narration.eventSet)


def filterEventsByChoice(choice_set: ChoiceSet, event_set: EventSet) -> EventSet:
    to_ret = EventSet()
    for event in event_set:
        if event.Choice in choice_set:
            to_ret.add(event)
    return to_ret


def filterEventsByPostStates(filter_func: FunctionType, event_set: EventSet) -> EventSet:
    to_ret = EventSet()
    for event in event_set:
        if filter_func(event.PostState):
            to_ret.add(event)
    return to_ret


def filterEventsByPreStates(filter_func: FunctionType, event_set: EventSet) -> EventSet:
    to_ret = EventSet()
    for event in event_set:
        if filter_func(event.PreState):
            to_ret.add(event)
    return to_ret


def ConvertGraphPathToNarrativePath(path, graph: nx.DiGraph) -> PathSet:
    states: List[NarrativeState] = []
    choiceListOfLists: List[List[NarrativeChoice]] = []

    for i in range(len(path)):
        states.append(path[i])

    for i in range(len(path) - 1):
        if i == 0:
            for ch_label in graph[states[i]][states[i + 1]]["choices"]:
                choiceListOfLists.append([ch_label])
        else:
            tempListOfList: List[List[NarrativeChoice]] = []
            for subList in choiceListOfLists:
                for ch_label in graph[states[i]][states[i + 1]]["choices"]:
                    tempList = subList
                    tempList.append(ch_label)
                    tempListOfList.append(tempList)
            choiceListOfLists = tempListOfList

    ret = PathSet()
    for choiceList in choiceListOfLists:
        ret.add(NarrativePath(states, choiceList))
    return ret


def pathsFromTo(model: NarrativeModel, from_states: StateSet, to_states: StateSet) -> PathSet:
    all_path = []
    for state in from_states:
        for path in nx.all_simple_paths(model.narrativeGraph,
                                        source=state,
                                        target=list(to_states)):
            all_path.append(path)

    ret = PathSet()
    for path in all_path:
        narrativePathSet = ConvertGraphPathToNarrativePath(path, model.narrativeGraph)
        ret = ret.union(narrativePathSet)

    return ret


def contains(to_contain: object, container: object) -> bool:
    if isinstance(container, StateSet) and isinstance(to_contain, NarrativeState):
        return to_contain in container

    elif isinstance(container, ChoiceSet) and isinstance(to_contain, NarrativeChoice):
        return to_contain in container

    elif isinstance(container, EventSet) and isinstance(to_contain, NarrativeEvent):
        return to_contain in container

    # searching for an State in a Narration
    elif isinstance(container, NarrativeModel) and isinstance(to_contain, NarrativeState):
        return to_contain in container.narrativeGraph.nodes

    # searching for a Choice in a Narration
    elif isinstance(container, NarrativeModel) and isinstance(to_contain, NarrativeChoice):
        for e in list(container.narrativeGraph.edges):
            u = e[0]
            v = e[1]
            if to_contain in container.narrativeGraph[u, v]['choices']:
                return True
        return False

    # searching for an Event in a Narration
    elif isinstance(container, NarrativeModel) and isinstance(to_contain, NarrativeEvent):
        if not container.narrativeGraph.has_edge(to_contain.PreState, to_contain.PostState):
            return False
        choiceSet: Set = container.narrativeGraph.edges[to_contain.PreState][to_contain.PostState]["choices"]
        if len(choiceSet) == 0:
            return False
        return to_contain.Choice in choiceSet

    # searching for a State in an EventSet
    elif isinstance(container, EventSet) and isinstance(to_contain, NarrativeState):
        for event in container:
            if event.PreState == to_contain or event.PostState == to_contain:
                return True
        return False

    # searching for a choice in an EventSet
    elif isinstance(container, EventSet) and isinstance(to_contain, NarrativeChoice):
        for event in container:
            if event.choice == to_contain:
                return True
        return False
    else:
        return False


# ================================================== Layout Generation =================================================

def ProcessPossibleNeighboursForModel(model: NarrativeModel, locationMappings: Dict) -> List:
    SpatialDependencyGraph = model.narrativeGraph.copy()

    for u in SpatialDependencyGraph.nodes:
        for v in SpatialDependencyGraph.nodes:
            if SpatialDependencyGraph.has_edge(u, v):
                choices_to_change = SpatialDependencyGraph[u][v]["choices"]
                if choices_to_change is not None:
                    for choice in locationMappings.keys():
                        if choice in choices_to_change:
                            try:
                                SpatialDependencyGraph[u][v]["locations"].add(locationMappings[choice])
                            except:
                                SpatialDependencyGraph[u][v]["locations"]: Set = {locationMappings[choice]}

    LocationSet = set(locationMappings.values())

    depth = {}
    frequencies = {}

    processed = []
    for l_1 in LocationSet:
        for l_2 in LocationSet:
            if l_1 != l_2:
                if (l_1, l_2) not in processed and (l_2, l_1) not in processed:
                    possible_neighbour = (l_1, l_2)
                    frequencies[possible_neighbour] = 0
                    depth[possible_neighbour] = -1
                    processed.append(possible_neighbour)

                    for n in SpatialDependencyGraph.nodes:
                        for n_in in SpatialDependencyGraph.predecessors(n):
                            for n_out in SpatialDependencyGraph.successors(n):
                                locationTags_in = SpatialDependencyGraph[n_in][n]["locations"]
                                locationTags_out = SpatialDependencyGraph[n][n_out]["locations"]
                                if (l_1 in locationTags_in and l_2 in locationTags_out) or (
                                        l_2 in locationTags_in and l_1 in locationTags_out):

                                    frequencies[possible_neighbour] = frequencies[possible_neighbour] + 1

                                    for initial in model.initialStates:
                                        length = nx.shortest_path_length(SpatialDependencyGraph, initial, n)
                                        if depth[possible_neighbour] > length or depth[possible_neighbour] == -1:
                                            depth[possible_neighbour] = length

    sorted_neighbours = sorted(processed, key=lambda x: (frequencies[x], depth[x]), reverse=True)
    return sorted_neighbours


def generateSparseLayoutForModel(model: NarrativeModel, locationMappings):
    neighbours = ProcessPossibleNeighboursForModel(model, locationMappings)
    layoutGraph: nx.Graph = nx.Graph()

    locationSet: Set = set(locationMappings.values())
    for location in locationSet:
        layoutGraph.add_node(location)

    i = 0
    while not nx.is_connected(layoutGraph):
        layoutGraph.add_edge(neighbours[i][0], neighbours[i][1])
        i = i + 1

    return layoutGraph


def generateHighConnectivityLayoutForModel(model: NarrativeModel, locationMappings):
    neighbours = ProcessPossibleNeighboursForModel(model, locationMappings)
    layoutGraph: nx.Graph = nx.Graph()

    locationSet: Set = set(locationMappings.values())
    for location in locationSet:
        layoutGraph.add_node(location)

    for a in locationSet:
        for b in locationSet:
            layoutGraph.add_edge(a, b)

    i = len(neighbours) - 1
    is_planar, embedding = nx.check_planarity(layoutGraph)
    while not is_planar:
        layoutGraph.remove_edge(neighbours[i][0], neighbours[i][1])
        is_planar, embedding = nx.check_planarity(layoutGraph)
        i = i - 1

    return layoutGraph


def drawLayoutGraph(layoutGraph):
    size = 200
    alpha = 1
    color = (0, 0, 0, alpha)

    pos = nx.planar_layout(layoutGraph)
    nx.draw(layoutGraph,
            pos=pos,
            with_labels=True,
            font_weight='bold',
            font_size='12',
            font_color=(0, 0, 0, 1),
            node_size=size,
            node_shape='o',
            node_color='w')

    plt.show()
