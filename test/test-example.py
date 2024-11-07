import random
from src.example import multiply_by_two

def test_multiply_by_two():
    # Test déterministe
    assert multiply_by_two(2) == 4
    assert multiply_by_two(0) == 0
    assert multiply_by_two(-3) == -6

    # Test avec des valeurs aléatoires
    for _ in range(5):  # Plusieurs tests avec des valeurs aléatoires
        x = random.randint(-100, 100)
        assert multiply_by_two(x) == x * 2
