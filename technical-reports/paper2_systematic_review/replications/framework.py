"""
Replication Framework: Shared utilities for all replications
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, Optional
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy import stats
import json
from datetime import datetime


@dataclass
class ReplicationResult:
    """Standardized result container for all replications."""
    paper_name: str
    method: str
    train_period: str
    test_period: str
    rmse: float
    mae: float
    direction_accuracy: float
    baseline_rmse: float
    rmse_improvement: float  # (baseline_rmse - rmse) / baseline_rmse
    granger_pvalue: Optional[float] = None
    n_train: int = 0
    n_test: int = 0
    timestamp: str = None
    notes: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'paper_name': self.paper_name,
            'method': self.method,
            'train_period': self.train_period,
            'test_period': self.test_period,
            'rmse': round(self.rmse, 6),
            'mae': round(self.mae, 6),
            'direction_accuracy': round(self.direction_accuracy, 4),
            'baseline_rmse': round(self.baseline_rmse, 6),
            'rmse_improvement': round(self.rmse_improvement, 4),
            'granger_pvalue': self.granger_pvalue,
            'n_train': self.n_train,
            'n_test': self.n_test,
            'timestamp': self.timestamp,
            'notes': self.notes,
        }


class DataPipeline:
    """Standardized data loading and preprocessing."""
    
    @staticmethod
    def ensure_dirs(base_dir: str = './data'):
        """Create required directories."""
        Path(base_dir).mkdir(parents=True, exist_ok=True)
        Path(f'{base_dir}/raw').mkdir(parents=True, exist_ok=True)
        Path(f'{base_dir}/processed').mkdir(parents=True, exist_ok=True)
        Path(f'{base_dir}/cache').mkdir(parents=True, exist_ok=True)
        Path('./results').mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def set_seeds(seed: int = 42):
        """Set all random seeds for reproducibility."""
        np.random.seed(seed)
        import random
        random.seed(seed)
        try:
            import torch
            torch.manual_seed(seed)
        except:
            pass
    
    @staticmethod
    def load_or_create_synthetic_data(n_samples: int = 4000, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate synthetic financial data for reproducible testing when real data unavailable.
        Simulates: date, text_sentiment, price_return, realized_volatility
        """
        np.random.seed(seed)
        
        # Generate AR(1) process for sentiment
        sentiment = np.zeros(n_samples)
        sentiment[0] = np.random.normal(0, 1)
        for t in range(1, n_samples):
            sentiment[t] = 0.7 * sentiment[t-1] + 0.3 * np.random.normal(0, 1)
        
        # Generate returns with sentiment as predictor
        returns = 0.05 + 0.15 * sentiment + np.random.normal(0, 0.08, n_samples)
        
        # Create time index
        dates = pd.date_range('1984-01-01', periods=n_samples, freq='D')
        
        df = pd.DataFrame({
            'date': dates,
            'sentiment': sentiment,
            'returns': returns,
        })
        
        # Split: 80/20
        split_idx = int(0.8 * len(df))
        train_df = df[:split_idx].reset_index(drop=True)
        test_df = df[split_idx:].reset_index(drop=True)
        
        return train_df, test_df


class EvaluationMetrics:
    """Standard evaluation for all models."""
    
    @staticmethod
    def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_baseline: Optional[np.ndarray] = None) -> dict:
        """
        Compute standard metrics.
        
        Args:
            y_true: Actual values
            y_pred: Model predictions
            y_baseline: Baseline (e.g., AR(1)) predictions for improvement calculation
        """
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        
        # Direction accuracy: % of correct sign predictions
        actual_direction = np.sign(y_true)
        pred_direction = np.sign(y_pred)
        direction_accuracy = np.mean(actual_direction == pred_direction)
        
        result = {
            'rmse': rmse,
            'mae': mae,
            'direction_accuracy': direction_accuracy,
        }
        
        # Improvement over baseline if provided
        if y_baseline is not None:
            baseline_rmse = np.sqrt(mean_squared_error(y_true, y_baseline))
            improvement = (baseline_rmse - rmse) / baseline_rmse
            result['baseline_rmse'] = baseline_rmse
            result['rmse_improvement'] = improvement
        
        return result
    
    @staticmethod
    def granger_causality_test(sentiment: np.ndarray, returns: np.ndarray, maxlag: int = 5) -> dict:
        """
        Simplified Granger causality test: Does lagged sentiment predict returns?
        Returns p-value indicating significance.
        """
        try:
            from statsmodels.tsa.stattools import grangercausalitytests
            data = np.column_stack([returns, sentiment])
            gc = grangercausalitytests(data, maxlag, verbose=False)
            
            # Extract p-value for lag 1
            pvalue = gc[1][0][0, 1]  # F-statistic p-value for lag 1
            return {'granger_pvalue': pvalue, 'granger_significant': pvalue < 0.05}
        except Exception as e:
            return {'granger_pvalue': None, 'granger_significant': None, 'error': str(e)}
    
    @staticmethod
    def diebold_mariano_test(error1: np.ndarray, error2: np.ndarray) -> dict:
        """
        Compare two forecasting methods: DM statistic for H0: both equally accurate.
        """
        try:
            from scipy.stats import norm
            loss_diff = error1**2 - error2**2
            mean_diff = np.mean(loss_diff)
            var_diff = np.var(loss_diff, ddof=1)
            dm_stat = mean_diff / np.sqrt(var_diff / len(loss_diff))
            pvalue = 2 * (1 - norm.cdf(np.abs(dm_stat)))
            return {'dm_statistic': dm_stat, 'dm_pvalue': pvalue, 'model1_better': dm_stat > 0}
        except Exception as e:
            return {'dm_statistic': None, 'dm_pvalue': None, 'error': str(e)}


class ResultLogger:
    """Log and compare results across replications."""
    
    def __init__(self, output_dir: str = './results'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: list[ReplicationResult] = []
    
    def add_result(self, result: ReplicationResult):
        """Add a replication result."""
        self.results.append(result)
        print(f"✓ {result.paper_name}: RMSE={result.rmse:.4f}, Improvement={result.rmse_improvement:.2%}")
    
    def save_results_json(self, filename: str = 'phase1_results.json'):
        """Save all results to JSON."""
        results_list = [r.to_dict() for r in self.results]
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(results_list, f, indent=2)
        print(f"\n✓ Results saved to {output_path}")
        return output_path
    
    def save_results_csv(self, filename: str = 'phase1_results.csv'):
        """Save all results to CSV."""
        results_df = pd.DataFrame([r.to_dict() for r in self.results])
        output_path = self.output_dir / filename
        results_df.to_csv(output_path, index=False)
        print(f"✓ Results saved to {output_path}")
        return output_path
    
    def print_summary(self):
        """Print summary table."""
        print("\n" + "="*80)
        print("PHASE 1 REPLICATION RESULTS SUMMARY")
        print("="*80)
        
        for result in self.results:
            print(f"\n{result.paper_name}")
            print(f"  Method: {result.method}")
            print(f"  Train: {result.train_period} (N={result.n_train})")
            print(f"  Test:  {result.test_period} (N={result.n_test})")
            print(f"  Metrics:")
            print(f"    RMSE: {result.rmse:.6f} (baseline: {result.baseline_rmse:.6f})")
            print(f"    Improvement: {result.rmse_improvement:.2%}")
            print(f"    MAE: {result.mae:.6f}")
            print(f"    Direction Accuracy: {result.direction_accuracy:.2%}")
            if result.granger_pvalue is not None:
                print(f"    Granger p-value: {result.granger_pvalue:.4f}")
            if result.notes:
                print(f"  Notes: {result.notes}")
