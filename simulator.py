import random

def monte_carlo_strategy(trials=1000):
    results = [random.choice(['Win','Lose']) for _ in range(trials)]
    return sum(r == 'Win' for r in results) / trials
