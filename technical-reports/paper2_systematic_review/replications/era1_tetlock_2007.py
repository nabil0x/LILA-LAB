"""
Tetlock (2007): Dictionary-based Sentiment via General Inquirer + PCA
Replicates: Wall Street Journal column → Stock returns prediction
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from typing import Tuple
import warnings

from framework import DataPipeline, EvaluationMetrics, ReplicationResult, ResultLogger

warnings.filterwarnings('ignore')


class GeneralInquirerEncoder:
    """
    Encode text using General Inquirer dictionary approach.
    Tetlock uses 77 word categories from Harvard IV-4 psychosocial dictionary.
    For replication: simulate 77 categories via simplified keyword grouping.
    """
    
    # Simplified GI categories (real version has 77)
    CATEGORIES = {
        'positive': ['good', 'great', 'excellent', 'strong', 'growth', 'gain', 'profit', 'success'],
        'negative': ['bad', 'weak', 'poor', 'decline', 'loss', 'fail', 'crisis', 'problem'],
        'uncertain': ['uncertain', 'unclear', 'unknown', 'doubt', 'risk', 'fear', 'concern'],
        'financial': ['stock', 'market', 'price', 'dollar', 'money', 'buy', 'sell'],
        'activity': ['trading', 'activity', 'active', 'movement', 'volatile'],
        'causality': ['caused', 'leading', 'effect', 'result', 'consequence'],
        'power': ['strong', 'weak', 'powerful', 'control', 'dominance'],
        'negation': ['not', 'no', 'never', 'neither', 'cannot'],
    }
    
    def __init__(self, n_categories: int = 77):
        """
        Args:
            n_categories: Number of GI categories (real: 77; simulation: 8-20)
        """
        self.n_categories = min(n_categories, len(self.CATEGORIES))
        self.category_names = list(self.CATEGORIES.keys())[:self.n_categories]
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode single text into category vector.
        Returns: (n_categories,) array of keyword counts
        """
        text = text.lower()
        vector = np.zeros(len(self.category_names))
        
        for idx, category in enumerate(self.category_names):
            for keyword in self.CATEGORIES[category]:
                vector[idx] += text.count(keyword)
        
        return vector
    
    def encode_batch(self, texts: list[str]) -> np.ndarray:
        """Encode batch of texts. Returns: (n_texts, n_categories)"""
        return np.array([self.encode_text(t) for t in texts])


class TetlockSentimentModel:
    """
    Reproduce Tetlock (2007):
    1. Extract GI word categories from financial news
    2. Compute PCA → pessimism factor (PC1)
    3. Forecast next-day stock returns via VAR
    """
    
    def __init__(self, n_gi_categories: int = 16, pca_components: int = 1, 
                 daily_recentering: bool = True):
        self.encoder = GeneralInquirerEncoder(n_categories=n_gi_categories)
        self.n_gi_categories = n_gi_categories
        self.pca_components = pca_components
        self.daily_recentering = daily_recentering
        
        self.pca = PCA(n_components=pca_components)
        self.scaler = StandardScaler()
        self.regression_model = LinearRegression()
        self.is_fit = False
    
    def fit(self, texts_train: np.ndarray, returns_train: np.ndarray):
        """
        Fit PCA and regression on training data.
        
        Args:
            texts_train: (n_train,) array of news texts
            returns_train: (n_train,) array of next-day returns
        """
        # Encode texts
        gi_categories = self.encoder.encode_batch(texts_train)  # (n, n_categories)
        
        # Standardize by day (Tetlock: "re-centered by day of week")
        if self.daily_recentering:
            gi_categories = self.scaler.fit_transform(gi_categories)
        
        # PCA to extract pessimism factor
        pessimism_factors = self.pca.fit_transform(gi_categories)  # (n, 1)
        
        # Regression: lag(pessimism) → returns
        # Use lagged pessimism
        X = pessimism_factors[:-1]  # lag
        y = returns_train[1:]  # current
        
        self.regression_model.fit(X, y)
        self.is_fit = True
        
        return self
    
    def predict(self, texts_test: np.ndarray) -> np.ndarray:
        """
        Predict returns from test texts.
        
        Args:
            texts_test: (n_test,) array of news texts
            
        Returns:
            (n_test-1,) array of predicted returns (lagged)
        """
        if not self.is_fit:
            raise ValueError("Model not fit. Call fit() first.")
        
        # Encode
        gi_categories = self.encoder.encode_batch(texts_test)
        
        # Standardize
        if self.daily_recentering:
            gi_categories = self.scaler.transform(gi_categories)
        
        # PCA
        pessimism_factors = self.pca.transform(gi_categories)
        
        # Lag and predict
        X = pessimism_factors[:-1]
        predictions = self.regression_model.predict(X)
        
        return predictions


def generate_synthetic_wsj_data(n_days: int = 4000, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic WSJ-like data for reproducible testing.
    Simulates: daily news text + next-day stock returns.
    """
    np.random.seed(seed)
    
    news_templates = [
        "Stock market saw {}activity today with prices {}.", 
        "Traders reported {}sentiment toward financial markets.",
        "Market uncertainty {}as investors faced {}conditions.",
        "Strong {} and {} trading patterns emerged.",
    ]
    
    descriptors = [
        ("strong positive", "rising"), ("weak negative", "falling"),
        ("moderate", "stable"), ("high uncertainty", "volatile"),
        ("bullish", "upward"), ("bearish", "downward"),
    ]
    
    texts = []
    true_sentiment = np.zeros(n_days)
    returns = np.zeros(n_days)
    
    # AR(1) sentiment process
    sentiment = 0
    for t in range(n_days):
        sentiment = 0.7 * sentiment + 0.3 * np.random.normal(0, 1)
        true_sentiment[t] = sentiment
        
        # Generate text with sentiment
        template = np.random.choice(news_templates)
        desc_idx = np.random.randint(0, len(descriptors))
        desc1, desc2 = descriptors[desc_idx]
        text = template.format(desc1, desc2)
        texts.append(text)
        
        # Generate returns: driven by lagged sentiment + noise
        if t > 0:
            returns[t] = 0.05 + 0.15 * true_sentiment[t-1] + np.random.normal(0, 0.08)
        else:
            returns[t] = np.random.normal(0, 0.08)
    
    dates = pd.date_range('1984-01-01', periods=n_days, freq='B')
    
    df = pd.DataFrame({
        'date': dates,
        'text': texts,
        'returns': returns,
    })
    
    # Split: 80/20
    split_idx = int(0.8 * len(df))
    train_df = df[:split_idx].reset_index(drop=True)
    test_df = df[split_idx:].reset_index(drop=True)
    
    return train_df, test_df


def run_tetlock_replication():
    """Execute full Tetlock (2007) replication."""
    
    print("\n" + "="*80)
    print("REPLICATING: Tetlock (2007) - Dictionary-based Sentiment")
    print("="*80)
    
    # Setup
    DataPipeline.ensure_dirs()
    DataPipeline.set_seeds(42)
    
    logger = ResultLogger()
    
    # Data
    print("\nGenerating synthetic WSJ data...")
    train_df, test_df = generate_synthetic_wsj_data(n_days=4000)
    print(f"  Train: {len(train_df)} days ({train_df['date'].min().date()} to {train_df['date'].max().date()})")
    print(f"  Test:  {len(test_df)} days ({test_df['date'].min().date()} to {test_df['date'].max().date()})")
    
    # Model
    print("\nFitting Tetlock sentiment model...")
    model = TetlockSentimentModel(n_gi_categories=16, pca_components=1, daily_recentering=True)
    model.fit(train_df['text'].values, train_df['returns'].values)
    
    # Predictions
    print("Generating predictions...")
    y_pred = model.predict(test_df['text'].values)
    y_true = test_df['returns'].values[1:]  # lagged
    
    # Baseline: AR(1)
    y_baseline = np.zeros_like(y_true)
    for i in range(len(y_baseline)):
        if i > 0:
            y_baseline[i] = 0.7 * y_true[i-1]
        else:
            y_baseline[i] = y_true[0]
    
    # Evaluate
    print("\nEvaluating...")
    metrics = EvaluationMetrics.compute_metrics(y_true, y_pred, y_baseline)
    
    granger_result = EvaluationMetrics.granger_causality_test(
        train_df['returns'].values[:-1], 
        train_df['returns'].values[1:],
        maxlag=1
    )
    
    # Result
    result = ReplicationResult(
        paper_name='Tetlock (2007)',
        method='Dictionary (GI) + PCA + VAR',
        train_period=f"{train_df['date'].min().date()} to {train_df['date'].max().date()}",
        test_period=f"{test_df['date'].min().date()} to {test_df['date'].max().date()}",
        rmse=metrics['rmse'],
        mae=metrics['mae'],
        direction_accuracy=metrics['direction_accuracy'],
        baseline_rmse=metrics['baseline_rmse'],
        rmse_improvement=metrics['rmse_improvement'],
        granger_pvalue=granger_result.get('granger_pvalue'),
        n_train=len(train_df),
        n_test=len(test_df),
        notes=f"GI categories: 16, Recentering: daily, Baseline: AR(1)"
    )
    
    logger.add_result(result)
    logger.save_results_json('tetlock_2007.json')
    logger.print_summary()
    
    return result


if __name__ == '__main__':
    result = run_tetlock_replication()
