from ravi.Ravi import *

wood_from_every_tree = 7
metal_from_every_mine = 5

wood_for_bow = 2
metal_for_bow = 1
wood_for_sword = 1
metal_for_sword = 2

tree_cutting_duration = 1
mine_digging_duration = 1
bow_making_duration = 1
sword_making_duration = 1

class_player = EntityClass()
class_player.addProperty("WOOD", int, 0)
class_player.addProperty("METAL", int, 0)
class_player.addProperty("BOW", int, 0)
class_player.addProperty("SWORD", int, 0)

class_world = EntityClass()
class_world.addProperty("TREE", int, 6)
class_world.addProperty("MINE", int, 4)
class_world.addProperty("REMAINING_DAYS", int, 5)

context = NarrativeContext()
context.addEntity("PLAYER", class_player)
context.addEntity("WORLD", class_world)


# =================================================== PreConditions ====================================================


def can_cut_tree(s: NarrativeState) -> bool:
    return s.getValue("WORLD", "TREE") > 0 and \
           s.getValue("WORLD", "REMAINING_DAYS") >= tree_cutting_duration


def can_dig_mine(s: NarrativeState) -> bool:
    return s.getValue("WORLD", "MINE") > 0 and \
           s.getValue("WORLD", "REMAINING_DAYS") >= mine_digging_duration


def can_make_bow(s: NarrativeState) -> bool:
    return s.getValue("PLAYER", "WOOD") >= wood_for_bow and \
           s.getValue("PLAYER", "METAL") >= metal_for_bow and \
           s.getValue("WORLD", "REMAINING_DAYS") >= bow_making_duration


def can_make_sword(s: NarrativeState) -> bool:
    return s.getValue("PLAYER", "WOOD") >= wood_for_sword and \
           s.getValue("PLAYER", "METAL") >= metal_for_sword and \
           s.getValue("WORLD", "REMAINING_DAYS") >= sword_making_duration


# ======================================================= Actions ======================================================


def cut_tree(s: NarrativeState) -> NarrativeState:
    newValue = s.getValue("PLAYER", "WOOD") + wood_from_every_tree
    s.setValue("PLAYER", "WOOD", newValue)

    newValue = s.getValue("WORLD", "REMAINING_DAYS") - tree_cutting_duration
    s.setValue("WORLD", "REMAINING_DAYS", newValue)
    return s


def dig_mine(s: NarrativeState) -> NarrativeState:
    newValue = s.getValue("PLAYER", "METAL") + metal_from_every_mine
    s.setValue("PLAYER", "METAL", newValue)

    newValue = s.getValue("WORLD", "REMAINING_DAYS") - mine_digging_duration
    s.setValue("WORLD", "REMAINING_DAYS", newValue)
    return s


def make_bow(s: NarrativeState) -> NarrativeState:
    newValue = s.getValue("PLAYER", "WOOD") - wood_for_bow
    s.setValue("PLAYER", "WOOD", newValue)

    newValue = s.getValue("PLAYER", "METAL") - metal_for_bow
    s.setValue("PLAYER", "METAL", newValue)

    newValue = s.getValue("PLAYER", "BOW") + 1
    s.setValue("PLAYER", "BOW", newValue)

    newValue = s.getValue("WORLD", "REMAINING_DAYS") - bow_making_duration
    s.setValue("WORLD", "REMAINING_DAYS", newValue)

    return s


def make_sword(s: NarrativeState) -> NarrativeState:
    newValue = s.getValue("PLAYER", "WOOD") - wood_for_sword
    s.setValue("PLAYER", "WOOD", newValue)

    newValue = s.getValue("PLAYER", "METAL") - metal_for_sword
    s.setValue("PLAYER", "METAL", newValue)

    newValue = s.getValue("PLAYER", "SWORD") + 1
    s.setValue("PLAYER", "SWORD", newValue)

    newValue = s.getValue("WORLD", "REMAINING_DAYS") - sword_making_duration
    s.setValue("WORLD", "REMAINING_DAYS", newValue)

    return s


# ====================================================== Choices =======================================================


ch_cut_tree = NarrativeChoice(can_cut_tree, cut_tree,
                              "CUT A TREE TO GET +%d WOOD (%d DAYS)" % (wood_from_every_tree, tree_cutting_duration)
                              )

ch_dig_mine = NarrativeChoice(can_dig_mine, dig_mine,
                              "DIG A MINE TO GET +%d METAL (%d DAYS)" % (metal_from_every_mine, mine_digging_duration)
                              )

ch_make_bow = NarrativeChoice(can_make_bow, make_bow,
                              "SPEND %d WOOD and %d METAL TO MAKE A BOW (%d DAYS)" % (wood_for_bow, metal_for_bow, bow_making_duration)
                              )

ch_make_sword = NarrativeChoice(can_make_sword, make_sword,
                                "SPEND %d WOOD and %d METAL TO MAKE A SWORD (%d DAYS)" % (wood_for_sword, metal_for_sword, sword_making_duration)
                                )

# =================================================== Assertions =======================================================

assertion_1 = NarrativeAssertion(
    "Number of WOOD should never become negative",
    lambda m: len(filterStates(lambda s: s.getValue("PLAYER", "WOOD") < 0,
                               statesOf(m)))
              == 0
)

assertion_2 = NarrativeAssertion(
    "Number of METAL should never become negative",
    lambda m: len(filterStates(lambda s: s.getValue("PLAYER", "METAL") < 0,
                               statesOf(m)))
              == 0
)


def calculate_success_Ratio(model: NarrativeModel) -> float:
    successPathCount = len(pathsFromTo(model,
                                       model.initialStates,
                                       filterStates(successCondition, statesOf(model))))

    failPathCount = len(pathsFromTo(model,
                                    model.initialStates,
                                    filterStates(failCondition, statesOf(model))))

    return successPathCount / (successPathCount + failPathCount)


assertion_3 = NarrativeAssertion(
    "5 percent < success ratio < 8 percent",
    lambda m: 0.05 < calculate_success_Ratio(m) < 0.08
)


# =============================================== Termination Conditions ===============================================


def failCondition(s: NarrativeState) -> bool:
    return s.getValue("WORLD", "REMAINING_DAYS") == 0


def successCondition(s: NarrativeState) -> bool:
    return s.getValue("PLAYER", "BOW") >= 1 and \
           s.getValue("PLAYER", "SWORD") >= 1


# ================================================== Narration Setting =================================================


initial_states = {NarrativeState(context)}
term_conditions = {failCondition, successCondition}
choices = [ch_cut_tree, ch_dig_mine, ch_make_bow, ch_make_sword]
assertions = [assertion_1, assertion_2, assertion_3]
settings: NarrationSetting = NarrationSetting(initial_states=initial_states,
                                              termination_conditions=term_conditions,
                                              choices=choices)

model: NarrativeModel = generateNarrativeModel(setting=settings, max_depth=math.inf)

# ======================================== Narration Generation and Proof Checking =====================================

model.validateAssertions(assertions=assertions)
print("SUCCESS RATIO: ", calculate_success_Ratio(model))
# print("TERMINABLE:", model.hasAbsoluteTermination())
# model.runNarration(True, NarrativeState(context))
#model.drawNarrationGraph(show_state=False, show_choices=True)
