# To be able to type classes defined later in the script
from __future__ import annotations
from typing import Iterator, Optional, List


class Direction:
    UP = "UP"
    DOWN = "DOWN"
    NOWHERE = "NOWHERE"


class Controller:
    def __init__(self) -> None:
        self.elevators: List[Elevator] = []

    def add_elevator(self, elevator: Elevator) -> None:
        """
        Adds an elevator to a controller.
        """
        self.elevators.append(elevator)

    def report_status(self) -> None:
        """
        A helper function that prints out useful elevator information.
        """
        for elevator in self.elevators:
            print(f"{elevator} is at {elevator.floor} floor.")
            print(f"{elevator}'s door are open: {elevator.door.is_open}")
            print(f"{elevator} is going: {elevator.direction}")
            print(
                f"People in the {elevator}: {[person.name for person in elevator.people]}"
            )

    @property
    def free_elevators(self) -> List[Elevator]:
        if not self.elevators:
            raise ValueError("No elevators in this controller")
        return [elevator for elevator in self.elevators if elevator.is_free]

    def elevator_for(self, person: Person) -> Optional[Elevator]:
        """Return an elevator if it is at the floor"""
        for elevator in self.elevators:
            if (
                elevator.floor == person.enter_floor
                and elevator.LOWEST_FLOOR <= person.exit_floor <= elevator.HIGHEST_FLOOR
            ):
                return elevator
        return None

    def call_elevator_for(self, person: Person) -> Optional[Elevator]:
        """
        Moves the 'best' elevator into a called floor. 
        Returns a True if moved and False if not elevator to be moved.
        """
        # Pick an elevator that is the closest and can travel to this floor
        best_elevator = None
        min_value = float("inf")
        for elevator in self.free_elevators:
            if (
                elevator.LOWEST_FLOOR <= person.enter_floor <= elevator.HIGHEST_FLOOR
                and elevator.LOWEST_FLOOR <= person.exit_floor <= elevator.HIGHEST_FLOOR
            ):
                floor_difference = abs(person.enter_floor - elevator.floor)
                if floor_difference < min_value:
                    min_value = floor_difference
                    best_elevator = elevator
        if not best_elevator:
            return None

        # Send an elevator
        best_elevator.move_to(person.enter_floor)
        return best_elevator

    def move_elevators(self) -> None:
        for elevator in self.elevators:
            elevator.move()


class Door:
    def __init__(self, is_open: bool = False) -> None:
        self.is_open: bool = is_open

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False


class Elevator:
    COUNTER = 0

    def __init__(self, lowest_floor: int, highest_floor: int) -> None:
        self.door: Door = Door()
        self.floor: int = 0  # Starts from ground level
        self.HIGHEST_FLOOR: int = highest_floor
        self.LOWEST_FLOOR: int = lowest_floor
        self.moving_to: Optional[int] = None  # If None it means that the lift is unused
        self.people: List[Person] = []

        self.validate()
        Elevator.COUNTER += 1
        self.id = Elevator.COUNTER

    def __str__(self) -> str:
        return f"Elevator nr.{self.id}"

    @property
    def is_free(self) -> bool:
        return not bool(self.moving_to)

    @property
    def stops(self) -> List[int]:
        """
        Returns a list of floors at which people inside the elevator
        want to get out.
        """
        return [person.exit_floor for person in self.people]

    @property
    def direction(self) -> str:
        """
        Returns the current direction in which the elvator is
        moving or null if not decided yet.
        """
        if not self.moving_to:
            return Direction.NOWHERE
        if self.moving_to > self.floor:
            return Direction.UP
        if self.moving_to < self.floor:
            return Direction.DOWN
        else:
            return Direction.NOWHERE

    @property
    def people_leaving(self) -> Iterator[Person]:
        """Returns a list of people leaving at this floor"""
        for person in self.people:
            if person.exit_floor == self.floor:
                yield person

    def move_to(self, floor: int) -> None:
        self.moving_to = floor

    def open_door(self) -> None:
        print(f"{self} door have opened")
        self.door.open()

    def close_door(self) -> None:
        print(f"{self} door have closed")
        self.door.close()

    def move(self) -> None:
        """
        Is an action method that should be used in a time frame.

        Each invocation represents one tick of time. 
        """
        if self.door.is_open:
            self.close_door()

        if stops := self.stop_queue:
            self.moving_to = stops[-1]

        if self.direction == Direction.UP:
            self.up_1()
        elif self.direction == Direction.DOWN:
            self.down_1()
        else:
            self.moving_to = None
            print(f"{self} is not moving this round")

    @property
    def stop_queue(self) -> Optional[List[int]]:
        """
        A property that represents the stop the current lift will do.

        Given people going in different direction it will create a stop
        route directed by the earliest request.
        """

        def filterUp(floor: int) -> bool:
            return floor > self.floor

        def filterDown(floor: int) -> bool:
            return floor < self.floor

        if not self.stops:
            return None

        oldest_request = self.stops[0]
        stop_queue = []
        if oldest_request > self.floor:
            stop_queue = list(filter(filterUp, self.stops))
        elif oldest_request < self.floor:
            stop_queue = list(filter(filterDown, self.stops))
        return stop_queue

    def validate(self) -> None:
        if type(self.LOWEST_FLOOR) != int or type(self.LOWEST_FLOOR) != int:
            raise ValueError("Invalid lowest floor")
        if self.LOWEST_FLOOR > 0:
            raise ValueError("Invalid lowest floor")
        if self.HIGHEST_FLOOR <= 0:
            raise ValueError("Invalid highest floor")
        if self.LOWEST_FLOOR >= self.HIGHEST_FLOOR:
            raise ValueError("Invalid elevator")

    def up_1(self) -> None:
        if self.door.is_open:
            raise ValueError("Cannot move the elevator if the door is not closed")
        if self.floor + 1 > self.HIGHEST_FLOOR:
            raise ValueError(f"Can't go higher that the {self.HIGHEST_FLOOR} floor")
        self.floor += 1
        print(f"{self} moved floors {self.floor -1} -> {self.floor}")

    def down_1(self) -> None:
        if self.door.is_open:
            raise ValueError("Cannot move the elevator if the door is not closed")
        if self.floor - 1 < self.LOWEST_FLOOR:
            raise ValueError(f"Can't go lower that the {self.LOWEST_FLOOR} floor")
        self.floor -= 1
        print(f"{self} moved floors {self.floor + 1} -> {self.floor}")


class Person:
    COUNTER = 0

    def __init__(self, name: str, enter_floor: int, exit_floor: int) -> None:
        self.name = name  # ID, might need to check if unique
        self.enter_floor = int(enter_floor)
        self.exit_floor = int(exit_floor)

        Person.COUNTER += 1
        self.id = Person.COUNTER

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return (
            f"<Person id:{self.id} -> {(self.name, self.enter_floor, self.exit_floor)}"
        )
