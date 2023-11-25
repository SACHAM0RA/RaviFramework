from ravi.Ravi import *

# character entity names
PLAYER: string = "player"
REBEL_LEADER: string = "rebel leader"
KING: string = "king"
KING_BROTHER: string = "king's brother"
PRISON_GUARD: string = "prison guard"

# location names
PRISON: string = "prison"
CITY: string = "city"
JUNGLE: string = "jungle"

FANTASY_LAND: string = "country"

# property names
LOCATION: string = "location"
IS_FREE: string = "is free"
IS_DEAD: string = "is dead"
IS_HEIR: string = "is heir"
MET_LEADER: string = "met with rebel leader"
MET_KING: string = "met with the king"
MET_KING_BROTHER: string = "met with the king's brother"
HELPED_REBELS: string = "helped rebels"
BETRAYED_REBELS: string = "betrayed rebels"
IS_KING: string = "is king"
IS_DEMOCRACY = "is democracy"
IS_CHANCELLOR = "is chancellor"
COUP_PLANNED = "coup is planned"

# ======================================================= Context ======================================================

class_player = EntityClass()
class_player.addProperty(IS_FREE, bool, False)
class_player.addProperty(LOCATION, str, PRISON)
class_player.addProperty(MET_LEADER, bool, False)
class_player.addProperty(MET_KING, bool, False)
class_player.addProperty(MET_KING_BROTHER, bool, False)
class_player.addProperty(HELPED_REBELS, bool, False)
class_player.addProperty(BETRAYED_REBELS, bool, False)
class_player.addProperty(IS_KING, bool, False)
class_player.addProperty(IS_CHANCELLOR, bool, False)
class_player.addProperty(IS_HEIR, bool, False)

class_country = EntityClass()
class_country.addProperty(IS_DEMOCRACY, bool, False)
class_country.addProperty(COUP_PLANNED, bool, False)

class_character = EntityClass()
class_character.addProperty(IS_DEAD, bool, False)
class_character.addProperty(IS_FREE, bool, True)
class_character.addProperty(IS_KING, bool, False)
class_character.addProperty(IS_HEIR, bool, False)
class_character.addProperty(LOCATION, str, NULL_STRING)

fantasyWorldContext = NarrativeContext()

fantasyWorldContext.addEntity(PLAYER, class_player)

fantasyWorldContext.addEntity(FANTASY_LAND, class_country)

fantasyWorldContext.addEntity(PRISON_GUARD, class_character)
fantasyWorldContext.setDefaultValue(PRISON_GUARD, LOCATION, PRISON)

fantasyWorldContext.addEntity(REBEL_LEADER, class_character)
fantasyWorldContext.setDefaultValue(REBEL_LEADER, LOCATION, JUNGLE)

fantasyWorldContext.addEntity(KING_BROTHER, class_character)
fantasyWorldContext.setDefaultValue(KING_BROTHER, LOCATION, PRISON)
fantasyWorldContext.setDefaultValue(KING_BROTHER, IS_FREE, False)
fantasyWorldContext.setDefaultValue(KING_BROTHER, IS_HEIR, True)

fantasyWorldContext.addEntity(KING, class_character)
fantasyWorldContext.setDefaultValue(KING, LOCATION, CITY)
fantasyWorldContext.setDefaultValue(KING, IS_KING, True)


# =================================================== PreConditions ====================================================


def isFree(w: NarrativeState) -> bool:
    return w.getValue(PLAYER, IS_FREE)


def isInPrison(w: NarrativeState) -> bool:
    return w.getValue(PLAYER, LOCATION) == PRISON


def isInJungle(w: NarrativeState) -> bool:
    return w.getValue(PLAYER, LOCATION) == JUNGLE


def isInCity(w: NarrativeState) -> bool:
    return w.getValue(PLAYER, LOCATION) == CITY


def hasMetRebelLeader(w: NarrativeState) -> bool:
    return w.getValue(PLAYER, MET_LEADER)


def hasMetKing(w: NarrativeState) -> bool:
    return w.getValue(PLAYER, MET_KING)


def hasMetKingBrother(w: NarrativeState) -> bool:
    return w.getValue(PLAYER, MET_KING_BROTHER)


def isThereAliveKing(w: NarrativeState) -> bool:
    return (w.getValue(KING, IS_KING) and not w.getValue(KING, IS_DEAD)) or \
           (w.getValue(KING_BROTHER, IS_KING) and not w.getValue(KING_BROTHER, IS_DEAD))


def hasBetrayedRebels(w: NarrativeState) -> bool:
    return w.getValue(PLAYER, BETRAYED_REBELS)


def isDemocracy(w: NarrativeState) -> bool:
    return w.getValue(FANTASY_LAND, IS_DEMOCRACY)


def youAreTheKing(w: NarrativeState) -> bool:
    return w.getValue(PLAYER, IS_KING)


def youAreTheChancellor(w: NarrativeState) -> bool:
    return w.getValue(PLAYER, IS_CHANCELLOR)


def coupeHasPlanned(w: NarrativeState) -> bool:
    return w.getValue(FANTASY_LAND, COUP_PLANNED)


def kingBrotherIsAlive(w: NarrativeState) -> bool:
    return not w.getValue(KING_BROTHER, IS_DEAD)


def kingIsAlive(w: NarrativeState) -> bool:
    return not w.getValue(KING, IS_DEAD)


# ======================================================= Actions ======================================================


def GoToJungle(w: NarrativeState) -> NarrativeState:
    w.setValue(PLAYER, LOCATION, JUNGLE)
    return w


def GoToCity(w: NarrativeState) -> NarrativeState:
    w.setValue(PLAYER, LOCATION, CITY)
    return w


def GoToPrison(w: NarrativeState) -> NarrativeState:
    w.setValue(PLAYER, LOCATION, PRISON)
    return w


def NegotiateWithGuard(w: NarrativeState) -> NarrativeState:
    w.setValue(PLAYER, IS_FREE, True)
    return w


def FightWithGuard(w: NarrativeState) -> NarrativeState:
    w.setValue(PLAYER, IS_FREE, True)
    w.setValue(PRISON_GUARD, IS_DEAD, True)
    return w


def MeetRebelLeader(w: NarrativeState) -> NarrativeState:
    w.setValue(PLAYER, MET_LEADER, True)
    return w


def MeetKingBrother(w: NarrativeState) -> NarrativeState:
    w.setValue(PLAYER, MET_KING_BROTHER, True)
    return w


def HelpRebelsAndKillTheKing(w: NarrativeState) -> NarrativeState:
    w.setValue(PLAYER, HELPED_REBELS, True)
    w.setValue(KING, IS_KING, False)
    w.setValue(KING, IS_DEAD, True)
    return w


def BetrayRebelsAndBecomeKing(w: NarrativeState) -> NarrativeState:
    w.setValue(PLAYER, BETRAYED_REBELS, True)
    w.setValue(PLAYER, IS_KING, True)
    return w


def BetrayRebelsAndBecomeChancellor(w: NarrativeState) -> NarrativeState:
    w.setValue(PLAYER, BETRAYED_REBELS, True)
    w.setValue(PLAYER, IS_CHANCELLOR, True)
    return w


def CreateDemocracy(w: NarrativeState) -> NarrativeState:
    w.setValue(FANTASY_LAND, IS_DEMOCRACY, True)
    return w


def PlanCoup(w: NarrativeState) -> NarrativeState:
    w.setValue(FANTASY_LAND, COUP_PLANNED, True)
    return w


def BetrayKingBrother(w: NarrativeState) -> NarrativeState:
    w.setValue(KING_BROTHER, IS_DEAD, True)
    w.setValue(KING_BROTHER, IS_HEIR, False)
    w.setValue(PLAYER, IS_HEIR, True)
    return w


def LeadTheCoupe(w: NarrativeState) -> NarrativeState:
    w.setValue(KING, IS_DEAD, True)
    w.setValue(KING, IS_KING, False)
    w.setValue(KING_BROTHER, IS_HEIR, False)
    w.setValue(KING_BROTHER, IS_KING, True)
    w.setValue(PLAYER, IS_HEIR, True)
    return w


# =============================================== Termination Conditions ===============================================


def TerminationCondition(w: NarrativeState) -> bool:
    return w.getValue(PLAYER, IS_KING) or \
           w.getValue(PLAYER, IS_HEIR) or \
           w.getValue(FANTASY_LAND, IS_DEMOCRACY)


# ====================================================== Choices =======================================================


choice_betray_rebels_chancellor = NarrativeChoice(lambda w: isInCity(w) and
                                                            hasMetRebelLeader(w) and
                                                            isThereAliveKing(w) and
                                                            not youAreTheChancellor(w),
                                                  BetrayRebelsAndBecomeChancellor,
                                                  "betray rebels and become the king's chancellor")

choice_plan_coupe = NarrativeChoice(lambda w: isInCity(w) and
                                              hasMetKingBrother(w) and
                                              youAreTheChancellor(w) and
                                              kingIsAlive(w) and
                                              not coupeHasPlanned(w),
                                    PlanCoup,
                                    "Free King's brother and plan a coupe against the king")

choice_help_rebels = NarrativeChoice(lambda w: isInCity(w) and
                                               hasMetRebelLeader(w) and
                                               isThereAliveKing(w) and
                                               not coupeHasPlanned(w),
                                     HelpRebelsAndKillTheKing,
                                     "help rebels and kill the king")

choice_negotiate_guard = NarrativeChoice(lambda w: not isFree(w) and isInPrison(w),
                                         NegotiateWithGuard,
                                         "Negotiate with prison guard")

choice_fight_guard = NarrativeChoice(lambda w: not isFree(w) and isInPrison(w),
                                     FightWithGuard,
                                     "Fight with prison guard")

choice_go_city = NarrativeChoice(lambda w: isFree(w) and not isInCity(w),
                                 GoToCity,
                                 "Go To the City")

choice_go_jungle = NarrativeChoice(lambda w: isFree(w) and not isInJungle(w),
                                   GoToJungle,
                                   "Go To the Jungle")

choice_go_prison = NarrativeChoice(lambda w: isFree(w) and not isInPrison(w),
                                   GoToPrison,
                                   "Go To the Prison")

choice_meet_king_brother = NarrativeChoice(lambda w: isFree(w) and isInPrison(w) and not hasMetKingBrother(w),
                                           MeetKingBrother,
                                           "Meet the king's brother")

choice_meet_rebel_leader = NarrativeChoice(lambda w: isInJungle(w) and not hasMetRebelLeader(w),
                                           MeetRebelLeader,
                                           "Meet the Rebel Leader")

choice_betray_rebels_become_king = NarrativeChoice(lambda w: isInCity(w) and
                                                             hasMetRebelLeader(w) and
                                                             not isThereAliveKing(w) and
                                                             not youAreTheKing(w) and
                                                             not isDemocracy(w),
                                                   BetrayRebelsAndBecomeKing,
                                                   "betray rebels and become the king")

choice_democracy = NarrativeChoice(lambda w: isInCity(w) and
                                             not isDemocracy(w) and
                                             not isThereAliveKing(w) and
                                             not youAreTheKing(w),
                                   CreateDemocracy,
                                   "create a democracy")

choice_betray_king_brother = NarrativeChoice(lambda w: isInCity(w) and
                                                       coupeHasPlanned(w) and
                                                       kingBrotherIsAlive(w) and
                                                       kingIsAlive(w) and
                                                       youAreTheChancellor(w),
                                             BetrayKingBrother,
                                             "Betray King's brother and scare the king about dangers of his brother")

choice_go_on_with_coup = NarrativeChoice(lambda w: isInCity(w) and
                                                   coupeHasPlanned(w) and
                                                   kingBrotherIsAlive(w) and
                                                   kingIsAlive(w) and
                                                   youAreTheChancellor(w),
                                         LeadTheCoupe,
                                         "lead the coupe and concede the crown to the king's brother")

# =================================================== Assertions =======================================================


assert_1 = NarrativeAssertion("It should be possible to end with democracy",
                              lambda model: len(
                                  filterStates(
                                      lambda w: w.getValue(FANTASY_LAND, IS_DEMOCRACY),
                                      statesOf(
                                          model))) != 0
                              )

assert_2 = NarrativeAssertion("It should be possible to end with being the king",
                              lambda model: len(
                                  filterStates(
                                      lambda w: w.getValue(PLAYER, IS_KING),
                                      statesOf(
                                          model))) != 0)

assert_3 = NarrativeAssertion("It should be possible to end with being the heir to the throne",
                              lambda model: len(
                                  filterStates(
                                      lambda w: w.getValue(PLAYER, IS_HEIR),
                                      statesOf(
                                          model))) != 0)

assert_4 = NarrativeAssertion(
    "It should be possible to end with democracy event if we choose to betray rebels at some point",
    lambda model: len(
        filterStates(
            lambda w: w.getValue(FANTASY_LAND, IS_DEMOCRACY),
            statesOf(
                subModelFrom(
                    postStatesOf(
                        filterEventsByChoice({choice_betray_rebels_chancellor},
                                             eventsIn(model))),
                    model)))) != 0)

assert_5 = NarrativeAssertion(
    "It should not be possible to end with democracy event if we choose to ally with king's brother",
    lambda model: len(
        filterStates(
            lambda w: w.getValue(FANTASY_LAND, IS_DEMOCRACY),
            statesOf(
                subModelFrom(
                    postStatesOf(
                        filterEventsByChoice({choice_plan_coupe},
                                             eventsIn(model))),
                    model)))) == 0)

assert_6 = NarrativeAssertion(
    "It should not be possible to choose to betray rebels and become chancellor but later choose to help them and kill the king",
    lambda model: len(filterEventsByChoice(
        {choice_help_rebels},
        eventsIn(
            subModelFrom(
                postStatesOf(
                    filterEventsByChoice({choice_betray_rebels_chancellor},
                                         eventsIn(model))),
                model)))) == 0)

# ================================================== Narration Setting =================================================


initial_states = {NarrativeState(fantasyWorldContext)}
term_conditions = {TerminationCondition}
choices = \
    [
        choice_negotiate_guard, choice_fight_guard, choice_go_city, choice_go_jungle, choice_go_prison,
        choice_meet_king_brother, choice_meet_rebel_leader, choice_help_rebels, choice_betray_rebels_become_king,
        choice_democracy, choice_betray_rebels_chancellor, choice_plan_coupe, choice_betray_king_brother,
        choice_go_on_with_coup
    ]
assertions = [assert_1, assert_2, assert_3, assert_4, assert_5, assert_6]

settings: NarrationSetting = NarrationSetting(initial_states=initial_states,
                                              termination_conditions=term_conditions,
                                              choices=choices)

# ======================================== Narration Generation and Proof Checking =====================================

model: NarrativeModel = generateNarrativeModel(setting=settings)

model.validateAssertions(assertions=assertions)
print("TERMINABLE:", model.hasAbsoluteTermination())
model.runNarration(False, initial_world_state=NarrativeState(fantasyWorldContext))
#model.drawNarrationGraph(show_state=False, show_choices=True)
