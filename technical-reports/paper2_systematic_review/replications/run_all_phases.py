"""
Master Runner: Execute all phases sequentially (Phase 1-4 + BENI integration)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from era1_tetlock_2007 import run_tetlock_replication
from era1_gentzkow_2019 import run_gentzkow_replication
from era2_ml_methods import run_ml_replication
from era3_transformers import run_transformer_replication
from era4_validation_framework import run_validation_framework
from framework import ResultLogger


def run_all_phases():
    """Execute Phases 1-4 sequentially."""
    
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  COMPREHENSIVE REPLICATION SUITE: 15-20 PAPERS ACROSS 4 ERAS  ".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    unified_logger = ResultLogger()
    
    # ============================================================================
    # PHASE 1: DICTIONARY-BASED
    # ============================================================================
    print("\n\n" + "▶ "*40)
    print("PHASE 1: DICTIONARY-BASED SENTIMENT (2007-2015)")
    print("▶ "*40)
    
    print("\n[1/2] Tetlock (2007)...")
    r1 = run_tetlock_replication()
    unified_logger.add_result(r1)
    
    print("\n[2/2] Gentzkow et al. (2019)...")
    r2 = run_gentzkow_replication()
    unified_logger.add_result(r2)
    
    # ============================================================================
    # PHASE 2: TRADITIONAL ML
    # ============================================================================
    print("\n\n" + "▶ "*40)
    print("PHASE 2: TRADITIONAL ML METHODS (2013-2019)")
    print("▶ "*40)
    
    ml_logger = run_ml_replication()
    for result in ml_logger.results:
        unified_logger.add_result(result)
    
    # ============================================================================
    # PHASE 3: TRANSFORMERS
    # ============================================================================
    print("\n\n" + "▶ "*40)
    print("PHASE 3: DEEP LEARNING / TRANSFORMERS (2018-2025)")
    print("▶ "*40)
    
    tf_logger = run_transformer_replication()
    for result in tf_logger.results:
        unified_logger.add_result(result)
    
    # ============================================================================
    # PHASE 4: VALIDATION FRAMEWORK
    # ============================================================================
    print("\n\n" + "▶ "*40)
    print("PHASE 4: VALIDATION FRAMEWORK & META-ANALYSIS")
    print("▶ "*40)
    
    synthesis = run_validation_framework()
    
    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    print("\n\n" + "="*80)
    print("FINAL SUMMARY: ALL PHASES COMPLETE")
    print("="*80)
    
    unified_logger.save_results_json('all_phases_unified_results.json')
    unified_logger.save_results_csv('all_phases_unified_results.csv')
    
    print(f"\n✓ Total replications: {len(unified_logger.results)}")
    print(f"✓ Median RMSE improvement: {np.median([r.rmse_improvement for r in unified_logger.results]):.2%}")
    print(f"✓ Mean direction accuracy: {np.mean([r.direction_accuracy for r in unified_logger.results]):.2%}")
    
    print(f"\nResults saved:")
    print(f"  - all_phases_unified_results.json")
    print(f"  - all_phases_unified_results.csv")
    print(f"  - reproducibility_checklist.json")
    print(f"  - meta_analysis_synthesis.json")
    
    return unified_logger


if __name__ == '__main__':
    import numpy as np
    logger = run_all_phases()
    
    print("\n\n" + "="*80)
    print("ALL PHASES EXECUTED SUCCESSFULLY")
    print("="*80)
