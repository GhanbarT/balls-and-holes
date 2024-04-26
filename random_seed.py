import hashlib
import os
import random
import time


# noinspection PyAttributeOutsideInit
class RandomSeed:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RandomSeed, cls).__new__(cls)
            cls._instance._seed = None
        return cls._instance

    def set_seed(self, seed=None):
        if seed is None:
            # Use a hash of the current time and process ID to seed the random number generator
            seed_str = f"{time.time()}_{os.getpid()}"
            seed = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16) % 10 ** 19
            random.seed(seed)
        else:
            random.seed(seed)
        self._seed = seed

    def get_seed(self):
        return self._seed
