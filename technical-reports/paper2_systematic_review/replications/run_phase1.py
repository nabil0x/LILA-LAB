"""
PHASE 1 Runner: Execute all dictionary-based replications
"""

import sys
from pathlib import Path

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

from era1_tetlock_2007 import run_tetlock_replication
from era1_gentzkow_2019 import run_gentzkow_replication
from framework import ResultLogger, ReplicationResult


def run_phase1():
    """Execute Phase 1: Dictionary-based foundation."""
    
    print("\n" + "="*80)
    print("PHASE 1: DICTIONARY-BASED SENTIMENT METHODS (2007-2019)")
    print("="*80)
    
    # Create unified logger
    logger = ResultLogger()
    
    # Run replications
    print("\n[1/2] Starting Tetlock (2007) replication...")
    result1 = run_tetlock_replication()
    logger.add_result(result1)
    
    print("\n[2/2] Starting Gentzkow et al. (2019) replication...")
    result2 = run_gentzkow_replication()
    logger.add_result(result2)
    
    # Summary
    logger.save_results_json('phase1_results.json')
    logger.save_results_csv('phase1_results.csv')
    logger.print_summary()
    
    print("\n" + "="*80)
    print("PHASE 1 COMPLETE")
    print("="*80)
    print(f"\n✓ Results saved to ./results/")
    print(f"✓ {len(logger.results)} replications completed")
    print(f"\nMedian RMSE Improvement: {np.median([r.rmse_improvement for r in logger.results]):.2%}")
    
    return logger


if __name__ == '__main__':
    import numpy as np
    logger = run_phase1()
