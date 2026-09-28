import abc
import functools
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")


def log_action(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        logging.info(f"{self.name} started perform_task.")
        try:
            return func(self, *args, **kwargs)
        finally:
            logging.info(f"{self.name} finished perform_task.")
    return wrapper


class InsufficientBatteryError(Exception):
    def __init__(self, name, required, available):
        self.name, self.required, self.available = name, required, available
        super().__init__(f"{name} needs {required}% battery for this task but only has {available}%.")


class Robot(abc.ABC):
    manufacturer = "RoboTech"
    population = 0

    def __init__(self, name, battery=100):
        self.name = name
        self.battery = battery
        Robot.population += 1

    @property
    def battery(self):
        return self._battery

    @battery.setter
    def battery(self, value):
        self._battery = max(0, min(100, value))

    def __str__(self):
        return f"{self.name} - {self.JOB} ({self.battery}% battery)"

    def __repr__(self):
        return f"{type(self).__name__}(name='{self.name}', battery={self.battery})"

    def use_battery(self, amount):
        if self.battery < amount:
            raise InsufficientBatteryError(self.name, amount, self.battery)
        self.battery -= amount

    @abc.abstractmethod
    def perform_task(self, **kwargs):
        pass

    @classmethod
    def from_config(cls, config):
        return cls(config.get("name", "Unnamed"), config.get("battery", 100))


class SanitizerBot(Robot):
    JOB = "Room Disinfection"

    def __init__(self, name, battery=100):
        super().__init__(name, battery)
        self.rooms = 3

    @log_action
    def perform_task(self, **kwargs):
        rooms = kwargs.get("rooms", 2)
        self.use_battery(8)
        return f"Disinfected {rooms} rooms."


class ScoutDrone(Robot):
    JOB = "Perimeter Surveillance"

    def __init__(self, name, battery=100):
        super().__init__(name, battery)
        self.max_distance = 100

    @log_action
    def perform_task(self, **kwargs):
        distance = kwargs.get("distance", 50)
        self.use_battery(15)
        return f"Surveilled {distance} meters."


def fleet_report(robots):
    for robot in robots:
        print(robot)


def run_task_safely(robot, **kwargs):
    try:
        result = robot.perform_task(**kwargs)
    except InsufficientBatteryError as e:
        logging.error(e)
    else:
        print(result)
    finally:
        print(f"{robot.name} battery: {robot.battery}%")


class SharedRobot:
    tasks = []

    def __init__(self, name):
        self.name = name

    def add_task(self, task):
        self.tasks.append(task)


class FixedRobot:
    def __init__(self, name):
        self.name, self.tasks = name, []

    def add_task(self, task):
        self.tasks.append(task)


def main():
    fleet = [SanitizerBot("Sharmaine", 80), ScoutDrone("Vanessa", 5)]

    print("=== ROBOT FLEET ===")
    print(f"Population: {Robot.population}")
    fleet_report(fleet)

    new_robot = ScoutDrone.from_config({"name": "Melanie", "battery": 100})
    fleet.append(new_robot)

    print(f"\nAdded {new_robot.name}")
    print(f"Population: {Robot.population}")

    print("\n=== TASKS ===")
    run_task_safely(fleet[0], rooms=3)
    run_task_safely(fleet[1], distance=40)

    print("\n=== DECORATOR CHECK ===")
    print(fleet[0].perform_task.__name__)
    print(fleet[0].perform_task.__doc__)

    a, b = SharedRobot("A"), SharedRobot("B")
    a.add_task("Cleaning")
    print("\n=== MUTABLE ATTRIBUTE BUG ===")
    print(a.tasks, b.tasks)

    c, d = FixedRobot("C"), FixedRobot("D")
    c.add_task("Cleaning")
    print("\n=== FIXED ===")
    print(c.tasks, d.tasks)


if __name__ == "__main__":
    main()






