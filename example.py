import DependencyInjection as DI


class Wheel:
    def __init__(self, wheel_type: str, ring_size: int, cost: float):
        self.wheel_type = wheel_type
        self.ring_size = ring_size
        self.cost = cost


class Brake:
    def __init__(self, system: str, cost: float):
        self.system = system
        self.cost = cost


class Engine:
    def __init__(self, manufacturer: str, is_turbo: bool, volume: int, cost: float):
        self.manufacturer = manufacturer
        self.is_turbo = is_turbo
        self.volume = volume
        self.cost = cost


# Initiate the Dependency Injector
di = DI

# initialize the di
di.initialize()

# Bind some classes to Injector
"""
In real world projects, we usually bind things like database instances, caches, etc
"""
di.bind(Brake, Brake(system='DISKS', cost=700.0))
di.bind(Wheel, Wheel(wheel_type='SPORT', ring_size=17, cost=5000.0))
di.bind(Engine, Engine(manufacturer='Saipa', is_turbo=False, volume=1500, cost=25000.0))


# params decorator will inject the bound classes to the function car_cost
@di.params(wheels=Wheel, brakes=Brake, engine=Engine)
def car_cost(wheels: Wheel, brakes: Brake, engine: Engine):
    return f'the car with Engine: {engine.manufacturer} and selected brake system and wheels ' \
           f'will cost: {wheels.cost + brakes.cost + engine.cost}'


# car_cost no need to get wheels, brakes and engine because this parameters are injected to it by di.
print(car_cost())

# let's clear the di and make a new car
di.clear()

# initialize the di
di.initialize()

# bind new instances
di.bind(Brake, Brake(system='ABS', cost=1900.0))
di.bind(Wheel, Wheel(wheel_type='SUPER SPORT', ring_size=18, cost=9000.0))
di.bind(Engine, Engine(manufacturer='Mercedes Benz', is_turbo=True, volume=2400, cost=45000.0))


# define the class Car
class Car:
    # Use Inject to inject car parts to the class
    wheels = DI.inject(Wheel)
    brakes = DI.inject(Brake)
    engine = DI.inject(Engine)

    def __init__(self, name, manufacturer):
        self.name = name
        self.manufacturer = manufacturer

    def cost(self):
        return f'Car Name: {self.name}, Car Manufacturer: {self.manufacturer}, ' \
               f'Car Cost: {self.wheels.cost + self.brakes.cost + self.engine.cost}'


new_car = Car(name='Omid', manufacturer='Koochaki Vehicle Manufacturers - KVM')

print(new_car.cost())
