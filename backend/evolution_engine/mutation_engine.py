import random
from backend.evolution_engine.genome_model import Genome


def mutate(genome: Genome) -> Genome:
    g = Genome(**genome.to_dict())
    g.ema_short = max(3, int(g.ema_short + random.gauss(0, 1)))
    g.ema_long = max(g.ema_short + 1, int(g.ema_long + random.gauss(0, 2)))
    g.risk_aggressiveness = max(0.1, g.risk_aggressiveness + random.gauss(0, 0.05))
    g.exploration_rate = min(0.9, max(0.01, g.exploration_rate + random.gauss(0, 0.02)))
    if random.random() < 0.05:
        g.exit_bias += random.choice([-1, 1]) * 0.1
    return g
