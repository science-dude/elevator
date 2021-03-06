import pytest

from elevator import Controller
from elevator import Door
from elevator import Elevator
from elevator import Person


class TestController:
    def test_add_elevator(self):
        controller = Controller()
        assert controller.elevators == []
        elevator = Elevator(0, 4)
        controller.add_elevator(elevator)
        assert controller.elevators[0] == elevator

    def test_free_elevators(self):
        pass

    def test_elevator_for(self):
        pass

    def test_call_elevator_for(self):
        pass

    def test_move_elevators(self):
        pass


class TestDoor:
    def test_initial(self):
        door = Door()
        assert not door.is_open

    def test_open(self):
        door = Door()
        door.open()
        assert door.is_open

    def test_close(self):
        door = Door(is_open=True)
        assert door.is_open
        door.close()
        assert not door.is_open


class TestElevator:
    def test_is_free(self):
        elevator = Elevator(0, 1)
        assert elevator.is_free
        elevator.moving_to = 1
        assert not elevator.is_free

    def test_invalid_elevator(self):
        Elevator(0, 1)
        with pytest.raises(ValueError):
            Elevator(1, 1)
        with pytest.raises(ValueError):
            Elevator(2, 1)
        with pytest.raises(ValueError):
            Elevator(-3, -2)
        with pytest.raises(ValueError):
            Elevator(1, 2)
        with pytest.raises(ValueError):
            Elevator(-1.2, 1)
        with pytest.raises(ValueError):
            Elevator("ground", "first")

    def test_cannot_go_above_highest_floor(self):
        elevator = Elevator(0, 1)
        elevator.up_1()
        with pytest.raises(ValueError) as error:
            elevator.up_1()
            assert str(error) == "Can't go higher that the 1"

    def test_cannot_move_if_doors_are_not_closed(self):
        elevator = Elevator(-2, 2)
        elevator.down_1()
        elevator.up_1()
        # Open door
        elevator.door.open()
        with pytest.raises(ValueError) as error:
            elevator.down_1()
        with pytest.raises(ValueError) as error:
            elevator.up_1()
        # Close door
        elevator.door.close()
        elevator.down_1()
        elevator.up_1()

    def test_cannot_go_below_lowest_floor(self):
        elevator = Elevator(0, 1)
        with pytest.raises(ValueError) as error:
            elevator.down_1()
            assert str(error) == "Can't go lower that the 0"

    def test_string_method(self):
        elevator = Elevator(0, 1)
        assert str(elevator) == f'Elevator nr.{elevator.id}'

    def test_open_door(self):
        # To be added if had time
        pass

    def test_close_door(self):
        # To be added if had time
        pass

    def test_people_leaving(self):
        # To be added if had time
        pass

    def test_stop_queue(self):
        # To be added if had time
        pass

    def test_stops(self):
        # To be added if had time
        pass

    def test_move_to(self):
        # To be added if had time
        pass

    def test_move(self):
        # To be added if had time
        pass


class TestPerson:
    def test_invalid(self):
        with pytest.raises(TypeError):
            Person()

        with pytest.raises(ValueError):
            Person("Joe", "first", "last")

        # Etc...

    def test_string_values(self):
        person = Person("Jack", "0", -1)
        assert person.enter_floor == 0
        assert person.exit_floor == -1

    def test_increment(self):
        current_count = Person.COUNTER
        Person("Jess", 0, 1)
        assert Person.COUNTER == current_count + 1

    def test_str(self):
        person = Person("Jess", 0, 1)
        assert str(person) == f"<Person id:{person.id} -> ('Jess', 0, 1)"
