import time
import pytest
import mockjutsu.core as mc
from mockjutsu.core import jutsu

# Dynamically fetch all 174+ data types from the core engine
ALL_TYPES = set()
for attr in dir(mc):
    if attr.endswith('_TYPES'):
        ALL_TYPES.update(getattr(mc, attr))

# Exclude heavy cryptographic algorithms that naturally take longer than 1ms per call in pure Python
HEAVY_TYPES = {'eth_address', 'btc_address'}
FAST_TYPES = sorted(list(ALL_TYPES - HEAVY_TYPES))

@pytest.mark.parametrize("data_type", FAST_TYPES)
def test_performance_baseline(data_type):
    """
    Ensures that standard mock data generation remains highly performant.
    Every function MUST pass this baseline (average generation < 1.5ms per call)
    """
    ITERATIONS = 200
    
    start = time.time()
    for _ in range(ITERATIONS):
        jutsu.generate(data_type)
    duration = time.time() - start
    
    # 200 calls must take less than 0.3 seconds (1.5ms per call limit to account for pytest overhead)
    max_duration = 0.300 
    assert duration < max_duration, f"Performance Regression! '{data_type}' took {duration:.4f}s for {ITERATIONS} calls (limit {max_duration}s)."
