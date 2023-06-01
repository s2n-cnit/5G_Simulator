import random
import sys
import numpy as np


class TrafficModel:
    def __init__(self):
        self.time_periodicity = 0  # ticks
        self.random_model = "Uniform Bounded"
        self.min_generation_instant = 1  # ticks
        self.max_generation_instant = 70  # Max aperiodic interval in ticks (it is modified afterwards in the main)
        self.last_random_generation = 0
        self.t_generation = None
        self.first_sample = self.t_generation
        self.last_gen = []
        self.apply_random_periodicity = {
            "Uniform": self.create_uniform_instance,
            "Uniform Bounded": self.create_uniform_bounded_instance
        }

    def get_variable_time_periodicity(self):
        if self.random_model in self.apply_random_periodicity:
            return self.apply_random_periodicity[self.random_model]()
        else:
            sys.exit("Random model " + self.random_model + " for the generation of the next packet "
                                                           "generation instant is not supported")

    def create_uniform_instance(self):
        return random.randint(self.min_generation_instant, self.max_generation_instant)

    def create_uniform_bounded_instance(self):
        t_random = random.randint(-2, 2)
        t = self.time_periodicity - self.last_random_generation + t_random
        # t = self.time_periodicity + t_random
        self.last_gen.append(t_random)
        if len(self.last_gen) > 2:
            del self.last_gen[0]
        self.last_random_generation = t_random
        return t

    def set_time_periodicity(self, time_period):
        self.time_periodicity = time_period
        self.t_generation = np.random.randint(0, time_period)   # Avoid to have UEs which transmit periodically
        # aligned in time

    def get_time_periodicity(self):
        return self.time_periodicity

    def set_random_model(self, random_model):
        self.random_model = random_model

    def get_random_model(self):
        return self.random_model

    def set_min_generation_instant(self, min_generation_instant: int):
        self.min_generation_instant = min_generation_instant

    def get_min_generation_instant(self):
        return self.min_generation_instant

    def set_max_generation_instant(self, max_generation_instant: int):
        self.max_generation_instant = max_generation_instant

    def get_max_generation_instant(self):
        return self.max_generation_instant


    
