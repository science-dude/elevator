import argparse
import sys
import time
from typing import List

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML

from elevator import Controller
from elevator import Elevator
from elevator import Person
from draw import Screen


bottom_toolbar = HTML(
    'Running elevator program, type <b><style bg="ansired">exit</style></b> to quit the program!'
)
session = PromptSession()


class Program:
    def __init__(
        self, controller: Controller, people: List[Person], description: str
    ) -> None:
        self.description: str = description
        self.lift_controller: Controller = controller
        self.people: List[Person] = people
        self.waiting_for_elevator: List[Person] = people

    def setup_for_drawing(self) -> None:
        """
        Creates a Screen instance that can be supplied with program's variables to draw the current elevator status
        """
        self.screen = Screen()

    def report_status(self) -> None:
        """Prints out the status of the program"""

        def names(people) -> List[str]:
            return [person.name for person in people]

        self.lift_controller.report_status()
        print(f"People waiting for a lift {names(self.waiting_for_elevator)}")

    def add_person_to_lift(self, elevator: Elevator, person: Person) -> None:
        """
        Moves a person into a lift. 

        TODO: Provide better abstractions for adding and removing people.
        """
        if not elevator.door.is_open:
            elevator.open_door()
        elevator.people.append(person)
        self.waiting_for_elevator.remove(person)
        print(f"{person.name} has entered the {elevator} at {elevator.floor} floor")

    def remove_person_to_lift(self, elevator: Elevator, person: Person) -> None:
        """
        Removes people from a lift. 

        TODO: Provide better abstractions removing people from a lift.
        """
        if not elevator.door.is_open:
            elevator.open_door()
        elevator.people.remove(person)

        # If there are not people in the lift, it is not moving nowhere
        if not elevator.people:
            elevator.moving_to = None
        print(f"{person.name} has {elevator} the lift at {elevator.floor} floor")

    def empty_line(self) -> None:
        print()

    def next(self) -> None:
        """
        Method triggering an action driven progression through a scenario.
        """
        # Remove people leaving at current floors
        for elevator in self.lift_controller.elevators:
            for person in elevator.people_leaving:
                self.remove_person_to_lift(elevator, person)

        self.empty_line()
        # Move people waiting into lifts if there is a lift at their floor
        for person in self.waiting_for_elevator:
            if elevator := self.lift_controller.elevator_for(person):
                self.add_person_to_lift(elevator, person)

        self.empty_line()
        # For people waiting on the lift calls the elevator
        for person in self.waiting_for_elevator:
            if elevator := self.lift_controller.call_elevator_for(person):
                print(f"An {elevator} for {person.name} is on its way!")
            else:
                print(f"No elevator for {person.name} at the moment")

        self.empty_line()
        # Action elevators
        self.lift_controller.move_elevators()

    def handle_input(self, answer: str) -> None:
        """
        A method that handles the input and therefore program progress 
        """
        answer = answer.lower()
        if answer in ["", "next"]:
            self.next()
        elif answer in ["new"]:
            self.enter_a_person()
        elif answer in ["s", "status"]:
            self.report_status()
        else:
            print(f"No action for '{answer}'")
        if hasattr(self, "screen"):
            # self.screen.draw()
            print("Drawing")

    def enter_a_person(self) -> None:
        """
        On being called takes input and adds a person to the waiting people
        """
        name = session.prompt("> ", bottom_toolbar=HTML("Enter a person's name"))
        enter_floor = session.prompt(
            "> ", bottom_toolbar=HTML("The floor they called the elevator")
        )
        exit_floor = session.prompt(
            "> ", bottom_toolbar=HTML("The floor they need to exit")
        )
        self.people.append(Person(name, enter_floor, exit_floor))


scenario_1 = Program(
    controller=Controller(),
    people=[
        Person("John", 0, 3),
        Person("Jack", 0, 4),
        Person("Jackson", 2, -1),
        Person("Janet", 2, 3),
    ],
    description="Basic scenario with 4 people and 1 lift",
)
scenario_1.lift_controller.add_elevator(Elevator(-1, 4))


scenario_2 = Program(
    controller=Controller(),
    people=[
        Person("John", 1, 3),
        Person("Jack", 0, -2),
        Person("Jackson", 2, -1),
        Person("Janet", 2, 3),
    ],
    description="Scenario at which the first person in the list of people is not at the ground floor",
)
scenario_2.lift_controller.add_elevator(Elevator(-3, 5))


scenario_3 = Program(
    controller=Controller(),
    people=[
        Person("John", 1, 3),
        Person("Jack", 0, -2),
        Person("Jackson", 2, -1),
        Person("Janet", 2, 3),
        Person("Joe", -3, 5),
        Person("Jonathan", -1, 6),
    ],
    description="Scenario with 2 lifts and 6 people",
)
scenario_3.lift_controller.add_elevator(Elevator(-3, 5))
scenario_3.lift_controller.add_elevator(Elevator(-1, 6))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs the elevator program.")
    parser.add_argument(
        "--draw",
        action="store_true",
        help="If provided script will draw the elevator movement",
    )
    args = parser.parse_args()

    scenarios = [scenario_1, scenario_2, scenario_3]

    for index, scenario in enumerate(scenarios):
        print(f"{index + 1}. - {scenario.description}")
    answer = session.prompt(
        "> ",
        bottom_toolbar=HTML(
            "Pick a scenario from the listed ones or amend the code and your own."
        ),
    )

    try:
        scenario = scenarios[int(answer) - 1]
    except Exception:
        print("No such scenario")
        sys.exit()

    program = scenario

    print(args)
    if args.draw:
        program.setup_for_drawing()

    while True:
        answer = session.prompt("> ", bottom_toolbar=bottom_toolbar)
        if answer == "exit":
            break
        try:
            program.handle_input(answer=answer)
        except ValueError as error:
            print(error)

        # Avoid cooking CPU
        time.sleep(0.01)

