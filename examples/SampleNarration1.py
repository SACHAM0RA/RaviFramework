from enum import *

from networkx import *

from ravi.Ravi import *


# ======================================================= Context ======================================================

class organization(Enum):
    none = 1
    order = 2
    army = 3
    clan = 4


class world_status(Enum):
    anarchy = 1
    tyranny = 2
    freedom = 3
    none = 4


class_character = EntityClass()
class_character.addProperty("IS_ALIVE", bool, True)

class_player = inherit_from(class_character)
class_player.addProperty("ALLIANCE", organization, organization.none)

class_world = EntityClass()
class_world.addProperty("STATUS", world_status, world_status.none)

context = NarrativeContext()
context.addEntity("PLAYER", class_player)
context.addEntity("PRECEPTOR", class_character)
context.addEntity("GENERAL", class_character)
context.addEntity("WORLD", class_world)


# =================================================== PreConditions ====================================================


def no_alliance(s: NarrativeState) -> bool:
    return s.getValue("PLAYER", "ALLIANCE") == organization.none


def member_of_army(s: NarrativeState) -> bool:
    return s.getValue("PLAYER", "ALLIANCE") == organization.army


def member_of_clan(s: NarrativeState) -> bool:
    return s.getValue("PLAYER", "ALLIANCE") == organization.clan


def can_fight_army(s: NarrativeState) -> bool:
    return s.getValue("PLAYER", "ALLIANCE") in {organization.order, organization.clan} and \
           s.getValue("GENERAL", "IS_ALIVE")


def can_fight_clan(s: NarrativeState) -> bool:
    return s.getValue("PLAYER", "ALLIANCE") in {organization.order, organization.army} and \
           s.getValue("PRECEPTOR", "IS_ALIVE")


def is_anarchy_possible(s: NarrativeState) -> bool:
    return s.getValue("PLAYER", "ALLIANCE") in {organization.order, organization.clan} and \
           not s.getValue("GENERAL", "IS_ALIVE")


def is_tyranny_possible(s: NarrativeState) -> bool:
    return s.getValue("PLAYER", "ALLIANCE") in {organization.order, organization.army} and \
           not s.getValue("PRECEPTOR", "IS_ALIVE")


def is_freedom_possible(s: NarrativeState) -> bool:
    return s.getValue("PLAYER", "ALLIANCE") == organization.order and \
           not s.getValue("PRECEPTOR", "IS_ALIVE") and \
           not s.getValue("GENERAL", "IS_ALIVE")


# ======================================================= Actions ======================================================


def join_army(s: NarrativeState) -> NarrativeState:
    s.setValue("PLAYER", "ALLIANCE", organization.army)
    return s


def join_clan(s: NarrativeState) -> NarrativeState:
    s.setValue("PLAYER", "ALLIANCE", organization.clan)
    return s


def establish_order(s: NarrativeState) -> NarrativeState:
    s.setValue("PLAYER", "ALLIANCE", organization.order)
    return s


def defeat_general(s: NarrativeState) -> NarrativeState:
    s.setValue("GENERAL", "IS_ALIVE", False)
    return s


def defeat_preceptor(s: NarrativeState) -> NarrativeState:
    s.setValue("PRECEPTOR", "IS_ALIVE", False)
    return s


def make_anarchy(s: NarrativeState) -> NarrativeState:
    s.setValue("WORLD", "STATUS", world_status.anarchy)
    return s


def make_tyranny(s: NarrativeState) -> NarrativeState:
    s.setValue("WORLD", "STATUS", world_status.tyranny)
    return s


def make_democracy(s: NarrativeState) -> NarrativeState:
    s.setValue("WORLD", "STATUS", world_status.freedom)
    return s


# ====================================================== Choices =======================================================


choice_join_army = NarrativeChoice(no_alliance, join_army,
                                   "JOIN THE ARMY OF VIRTUE")

choice_join_clan = NarrativeChoice(no_alliance, join_clan,
                                   "JOIN THE CLAN OF CHAOS")

choice_defeat_general = NarrativeChoice(can_fight_army, defeat_general,
                                        "FIGHT ARMY AND DEFEAT THE GENERAL")

choice_defeat_preceptor = NarrativeChoice(can_fight_clan, defeat_preceptor,
                                          "FIGHT CLAN AND DEFEAT THE PRECEPTOR")

choice_betray_clan = NarrativeChoice(member_of_clan, establish_order,
                                     "BETRAY CLAN AND ESTABLISH THE ORDER OF DOUBT")

choice_betray_army = NarrativeChoice(member_of_army, establish_order,
                                     "BETRAY ARMY AND ESTABLISH THE ORDER OF DOUBT")

choice_make_anarchy = NarrativeChoice(is_anarchy_possible, make_anarchy,
                                      "LIGHT UP THE FIRE OF ANARCHY ALL AROUND THE WORLD")

choice_make_tyranny = NarrativeChoice(is_tyranny_possible, make_tyranny,
                                      "CREATE A WORLD-WIDE TYRANNY OF VIRTUE")

choice_make_democracy = NarrativeChoice(is_freedom_possible, make_democracy,
                                        "SAVE HUMANITY FROM BOTH ANARCHY AND TYRANNY")

# =================================================== Assertions =======================================================

assertion_1 = NarrativeAssertion(
    "Possible to defeat the general even if the player chose to join the army at first",
    lambda model:
    choice_defeat_general in choicesOf(
        subModelFrom(
            postStatesOf(
                filterEventsByChoice(
                    {choice_join_army},
                    eventsIn(model)
                )
            ),
            model
        )
    )
)

assertion_2 = NarrativeAssertion(
    "Possible to end with anarchy even if the player chose to betray the clan",
    lambda model:
    len(
        filterStates(
            lambda s: s.getValue("WORLD", "STATUS") == world_status.anarchy,
            statesOf(
                subModelFrom(
                    postStatesOf(
                        filterEventsByChoice(
                            {choice_betray_clan},
                            eventsIn(model)
                        )
                    ),
                    model
                )
            )
        )
    ) != 0
)

assertion_3 = NarrativeAssertion(
    "Impossible to defeat the general if the player is still allied with the army",
    lambda model:
    len(
        filterStates(
            lambda s: s.getValue("PLAYER", "ALLIANCE") == organization.army,
            statesOf(
                preStatesOf(
                    filterEventsByChoice(
                        {choice_defeat_general},
                        eventsIn(model)
                    )
                )
            )
        )
    ) == 0
)


# =============================================== Termination Conditions ===============================================


def terminationCondition(s: NarrativeState) -> bool:
    return s.getValue("WORLD", "STATUS") != world_status.none


# ================================================== Narration Setting =================================================


initial_states = {NarrativeState(context)}
term_conditions = {terminationCondition}
choices = \
    [
        choice_join_army, choice_join_clan, choice_defeat_general,
        choice_defeat_preceptor, choice_make_anarchy, choice_make_tyranny,
        choice_betray_clan, choice_betray_army, choice_make_democracy
    ]
assertions = [assertion_1, assertion_2, assertion_3]

settings: NarrationSetting = NarrationSetting(initial_states=initial_states,
                                              termination_conditions=term_conditions,
                                              choices=choices)

model: NarrativeModel = generateNarrativeModel(setting=settings)

# ======================================== Narration Generation and Proof Checking =====================================

# model.validateAssertions(assertions=assertions)
# print("TERMINABLE:", model.hasAbsoluteTermination())
# model.runNarration(False, NarrativeState(context))
# model.drawNarrationGraph(show_state=False, show_choices=True)

LocationMappings = {choice_join_army: "MOUNTAINS",
                    choice_join_clan: "JUNGLE",
                    choice_defeat_general: "DESERT",
                    choice_defeat_preceptor: "RIVERSIDE",
                    choice_betray_clan: "SHORE",
                    choice_betray_army: "SHORE",
                    choice_make_anarchy: "CITY",
                    choice_make_tyranny: "CITY",
                    choice_make_democracy: "SHORE"}

sparse_layout = generateSparseLayoutForModel(model, LocationMappings)
drawLayoutGraph(sparse_layout)

high_connectivity_layout = generateHighConnectivityLayoutForModel(model, LocationMappings)
drawLayoutGraph(high_connectivity_layout)
