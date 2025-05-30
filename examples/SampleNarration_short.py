from enum import *

from networkx import *

from ravi.Ravi import *


# ======================================================= Context ======================================================

class edu_status(Enum):
    PHS_STUDENT = 1
    GRADUATED = 2
    NONE = 3


class_person = EntityClass()
class_person.addProperty("STATUS", edu_status, edu_status.PHS_STUDENT)
class_person.addProperty("IS_HOME", bool, True)

context = NarrativeContext()
context.addEntity("ME", class_person)


# =================================================== PreConditions ====================================================


def is_at_university(s: NarrativeState) -> bool:
    return s.getValue("ME", "IS_HOME") == False


def is_at_home(s: NarrativeState) -> bool:
    return s.getValue("ME", "IS_HOME") == True


def has_phd(s: NarrativeState) -> bool:
    return s.getValue("ME", "HAS_PHD") == True


# ======================================================= Actions ======================================================


def go_to_university(s: NarrativeState) -> NarrativeState:
    s.setValue("ME", "IS_HOME", False)
    return s


def study_for_phd(s: NarrativeState) -> NarrativeState:
    s.setValue("ME", "STATUS", edu_status.GRADUATED)
    s.setValue("ME", "IS_HOME", True)
    return s


def cancel_phd(s: NarrativeState) -> NarrativeState:
    s.setValue("ME", "STATUS", edu_status.NONE)
    s.setValue("ME", "IS_HOME", True)
    return s


# ====================================================== Choices =======================================================


choice_go_university = NarrativeChoice(is_at_home, go_to_university, "LEAVE HOME AND GO TO UNIVERSITY")
choice_study = NarrativeChoice(is_at_university, study_for_phd, "STUDY AT UNIVERSITY AND GET A PHD")
choice_cancel = NarrativeChoice(is_at_university, cancel_phd, "CANCEL PHD AND GO HOME")


# =================================================== Assertions =======================================================

def assertion_body(model: NarrativeModel) -> bool:
    all_events = eventsIn(model)
    only_study_events = filterEventsByChoice({choice_study}, all_events)
    before_study_states = preStatesOf(only_study_events)
    after_study_model = subModelFrom(before_study_states, model)
    all_after_study_states = statesOf(after_study_model)
    all_after_study_graduated_states = filterStates(lambda s: s.getValue("ME", "STATUS") == edu_status.GRADUATED, all_after_study_states)
    return len(all_after_study_graduated_states) != 0


assertion = NarrativeAssertion("IF YOU STUDY, YOU CAN GRADUATE", assertion_body)


# =============================================== Termination Conditions ===============================================


def terminationCondition(s: NarrativeState) -> bool:
    return s.getValue("ME", "STATUS") in {edu_status.GRADUATED, edu_status.NONE}


# ================================================== Narration Setting =================================================


initial_states = {NarrativeState(context)}
term_conditions = {terminationCondition}
choices = [
    choice_cancel,
    choice_go_university,
    choice_study
]

assertions = [assertion]

settings: NarrationSetting = NarrationSetting(initial_states=initial_states,
                                              termination_conditions=term_conditions,
                                              choices=choices)

# ======================================== Narration Generation and Proof Checking =====================================

model: NarrativeModel = generateNarrativeModel(setting=settings)

model.validateAssertions(assertions=assertions)
print("TERMINABLE:", model.hasAbsoluteTermination())
# model.runNarration(False, NarrativeState(context))
model.drawNarrationGraph(show_state=False, show_choices=True)

# ================================================== Map layout Generation =============================================