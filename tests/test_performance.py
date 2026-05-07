import time
import pytest
from mockjutsu.core import jutsu

def test_global_performance_baseline():
    """
    Ensures that standard mock data generation remains highly performant.
    Every new function MUST pass this baseline (average generation < 1ms per call)
    Excludes cryptographically heavy algorithms like keccak256 (eth_address).
    """
    # Test a sample of fast functions to ensure no regression
    fast_types = ['fullname', 'iban', 'cardnum', 'phone', 'tckn', 'taxid']
    
    for t in fast_types:
        start = time.time()
        for _ in range(1000):
            jutsu.generate(t)
        duration = time.time() - start
        
        # 1000 calls must take less than 1.0 second (1ms per call max)
        assert duration < 1.0, f"Performance Regression! '{t}' took {duration}s for 1000 calls."
