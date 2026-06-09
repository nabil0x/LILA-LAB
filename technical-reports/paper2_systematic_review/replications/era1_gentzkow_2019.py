"""
Gentzkow, Shapiro & Taddy (2019): Policy Uncertainty Index
Replicates: Newspaper text → Policy uncertainty proxy → GDP forecasting
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from typing import Tuple, Dict
import warnings

from framework import DataPipeline, EvaluationMetrics, ReplicationResult, ResultLogger

warnings.filterwarnings('ignore')


class PolicyUncertaintyExtractor:
    """
    Extract policy uncertainty from newspaper text using keyword approach.
    
    Mimics Gentzkow et al.: Define categories (fiscal, monetary, regulation, uncertainty)
    then count keywords and normalize to create uncertainty index.
    """
    
    KEYWORDS = {
        'fiscal': ['tax', 'spending', 'budget', 'deficit', 'revenue', 'appropriation', 
                   'expenditure', 'government spending', 'fiscal policy', 'balanced budget'],
        'monetary': ['interest rate', 'fed', 'central bank', 'monetary', 'quantitative easing',
                     'taper', 'liquidity', 'inflation target', 'reserve requirement'],
        'regulation': ['regulation', 'compliance', 'legal', 'lawsuit', 'penalty', 'SEC',
                       'EPA', 'OSHA', 'enforcement', 'regulatory', 'deregulation'],
        'uncertainty': ['uncertain', 'unclear', 'unpredictable', 'ambiguous', 'unknown',
                        'risky', 'unstable', 'volatility', 'shock', 'crisis'],
    }
    
    def __init__(self, normalize: str = 'zscore'):
        """
        Args:
            normalize: 'zscore' (per category) or 'total' (by total keywords)
        """
        self.normalize = normalize
        self.scaler = StandardScaler()
    
    def extract_features(self, texts: list[str]) -> np.ndarray:
        """
        Extract keyword counts by category.
        
        Args:
            texts: List of news texts
            
        Returns:
            (n_texts, n_categories) array of keyword counts
        """
        n_texts = len(texts)
        n_categories = len(self.KEYWORDS)
        features = np.zeros((n_texts, n_categories))
        
        category_names = list(self.KEYWORDS.keys())
        
        for i, text in enumerate(texts):
            text_lower = text.lower()
            for j, category in enumerate(category_names):
                count = 0
                for keyword in self.KEYWORDS[category]:
                    count += text_lower.count(keyword)
                features[i, j] = count
        
        return features, category_names
    
    def compute_epu_index(self, texts: list[str]) -> np.ndarray:
        """
        Compute Economic Policy Uncertainty index.
        
        Method: Average across category-normalized keyword counts.
        Returns: (n_texts,) array of EPU values
        """
        features, categories = self.extract_features(texts)
        
        # Normalize by category (z-score)
        features_normalized = self.scaler.fit_transform(features)
        
        # EPU index: average across categories
        epu_index = np.mean(np.abs(features_normalized), axis=1)
        
        return epu_index


class PolicyUncertaintyForecaster:
    """
    Forecast GDP growth using policy uncertainty index.
    Replicates Gentzkow et al.: EPU(t) → GDP(t+h)
    """
    
    def __init__(self, lags: int = 12, horizon: int = 1):
        """
        Args:
            lags: Number of lags for AR model (default: 12 months)
            horizon: Forecast horizon (default: 1 month ahead)
        """
        self.lags = lags
        self.horizon = horizon
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.is_fit = False
    
    def fit(self, epu_index: np.ndarray, gdp_growth: np.ndarray):
        """
        Fit model: lagged EPU + lagged GDP → current GDP.
        
        Args:
            epu_index: (n_periods,) EPU values
            gdp_growth: (n_periods,) GDP growth rates
        """
        n = len(epu_index)
        
        # Build lagged features
        X = np.zeros((n - self.lags - self.horizon, 2 * self.lags))
        y = np.zeros(n - self.lags - self.horizon)
        
        for i in range(self.lags, n - self.horizon):
            # Lags of EPU
            X[i - self.lags, :self.lags] = epu_index[i-self.lags:i]
            # Lags of GDP
            X[i - self.lags, self.lags:] = gdp_growth[i-self.lags:i]
            # Target: GDP at horizon
            y[i - self.lags] = gdp_growth[i + self.horizon]
        
        # Standardize
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_fit = True
        
        return self
    
    def predict(self, epu_index: np.ndarray, gdp_growth: np.ndarray) -> np.ndarray:
        """
        Predict GDP growth.
        
        Args:
            epu_index: (n_periods,) EPU values
            gdp_growth: (n_periods,) GDP growth rates
            
        Returns:
            (n_periods - lags - horizon,) predicted GDP growth
        """
        if not self.is_fit:
            raise ValueError("Model not fit. Call fit() first.")
        
        n = len(epu_index)
        X = np.zeros((n - self.lags - self.horizon, 2 * self.lags))
        
        for i in range(self.lags, n - self.horizon):
            X[i - self.lags, :self.lags] = epu_index[i-self.lags:i]
            X[i - self.lags, self.lags:] = gdp_growth[i-self.lags:i]
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)


def generate_synthetic_news_gdp_data(n_months: int = 360, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic news + GDP data for reproducible testing.
    Simulates: monthly newspaper articles + monthly GDP growth.
    """
    np.random.seed(seed)
    
    news_templates = {
        'fiscal': [
            "Congress debates {} budget proposal.",
            "Tax reform legislation faces {} challenges.",
            "Government spending {} amid fiscal concerns.",
        ],
        'monetary': [
            "Federal Reserve considers {} rate policy.",
            "Central bank uncertainty over {} targets.",
            "Monetary policy responses to {} conditions.",
        ],
        'regulation': [
            "New regulatory framework {} implementation.",
            "Compliance costs {} for businesses.",
            "Legal challenges to {} regulations.",
        ],
        'uncertainty': [
            "Market uncertainty {} over policy direction.",
            "Economic outlook remains {} and unclear.",
            "Political risks create {} in markets.",
        ],
    }
    
    texts = []
    gdp_growth = np.zeros(n_months)
    
    # AR(1) GDP process
    gdp = 2.0
    for t in range(n_months):
        # AR(1) + seasonal + shock
        gdp = 2.0 + 0.6 * (gdp - 2.0) + 0.3 * np.random.normal(0, 1)
        gdp_growth[t] = gdp
        
        # Generate news with intensity proportional to GDP volatility
        n_articles = np.random.randint(15, 35)  # ~5-10 articles per day * ~20 trading days
        
        articles_month = []
        for _ in range(n_articles):
            category = np.random.choice(list(news_templates.keys()))
            template = np.random.choice(news_templates[category])
            adjective = np.random.choice(['significant', 'growing', 'concerning', 'developing'])
            text = template.format(adjective)
            articles_month.append(text)
        
        # Combine into one "month" of news
        combined_text = " ".join(articles_month)
        texts.append(combined_text)
    
    dates = pd.date_range('1985-01-01', periods=n_months, freq='M')
    
    df = pd.DataFrame({
        'date': dates,
        'text': texts,
        'gdp_growth': gdp_growth,
    })
    
    # Split: 70% train, 30% test (typical for policy analysis)
    split_idx = int(0.70 * len(df))
    train_df = df[:split_idx].reset_index(drop=True)
    test_df = df[split_idx:].reset_index(drop=True)
    
    return train_df, test_df


def run_gentzkow_replication():
    """Execute full Gentzkow et al. (2019) replication."""
    
    print("\n" + "="*80)
    print("REPLICATING: Gentzkow, Shapiro & Taddy (2019) - Policy Uncertainty Index")
    print("="*80)
    
    # Setup
    DataPipeline.ensure_dirs()
    DataPipeline.set_seeds(42)
    
    logger = ResultLogger()
    
    # Data
    print("\nGenerating synthetic newspaper + GDP data...")
    train_df, test_df = generate_synthetic_news_gdp_data(n_months=360)
    print(f"  Train: {len(train_df)} months ({train_df['date'].min().date()} to {train_df['date'].max().date()})")
    print(f"  Test:  {len(test_df)} months ({test_df['date'].min().date()} to {test_df['date'].max().date()})")
    
    # EPU Index
    print("\nExtracting Policy Uncertainty Index...")
    epu_extractor = PolicyUncertaintyExtractor(normalize='zscore')
    
    epu_train = epu_extractor.compute_epu_index(train_df['text'].values)
    epu_test = epu_extractor.compute_epu_index(test_df['text'].values)
    print(f"  EPU (train): mean={epu_train.mean():.4f}, std={epu_train.std():.4f}")
    print(f"  EPU (test):  mean={epu_test.mean():.4f}, std={epu_test.std():.4f}")
    
    # Model with EPU
    print("\nFitting forecasting model WITH EPU...")
    model_with_epu = PolicyUncertaintyForecaster(lags=12, horizon=1)
    model_with_epu.fit(epu_train, train_df['gdp_growth'].values)
    
    y_pred_epu = model_with_epu.predict(epu_test, test_df['gdp_growth'].values)
    y_true_epu = test_df['gdp_growth'].values[12:12+len(y_pred_epu)]
    
    # Baseline model: GDP only (no EPU)
    print("Fitting baseline model WITHOUT EPU...")
    model_baseline = LinearRegression()
    
    n_train = len(train_df)
    lags = 12
    X_train = np.array([train_df['gdp_growth'].values[i-lags:i] for i in range(lags, n_train)])
    y_train = train_df['gdp_growth'].values[lags:]
    
    model_baseline.fit(X_train, y_train)
    
    n_test = len(test_df)
    X_test = np.array([test_df['gdp_growth'].values[i-lags:i] for i in range(lags, n_test)])
    y_pred_baseline = model_baseline.predict(X_test)
    y_true_baseline = test_df['gdp_growth'].values[lags:]
    
    # Align lengths
    n_eval = min(len(y_true_epu), len(y_pred_baseline))
    y_true = y_true_epu[:n_eval]
    y_pred = y_pred_epu[:n_eval]
    y_baseline = y_pred_baseline[:n_eval]
    
    # Evaluate
    print("\nEvaluating...")
    metrics = EvaluationMetrics.compute_metrics(y_true, y_pred, y_baseline)
    
    # Result
    result = ReplicationResult(
        paper_name='Gentzkow et al. (2019)',
        method='Policy Uncertainty Index (keyword-based)',
        train_period=f"{train_df['date'].min().date()} to {train_df['date'].max().date()}",
        test_period=f"{test_df['date'].min().date()} to {test_df['date'].max().date()}",
        rmse=metrics['rmse'],
        mae=metrics['mae'],
        direction_accuracy=metrics['direction_accuracy'],
        baseline_rmse=metrics['baseline_rmse'],
        rmse_improvement=metrics['rmse_improvement'],
        n_train=len(train_df),
        n_test=len(test_df),
        notes=f"EPU categories: 4 (fiscal, monetary, regulation, uncertainty), Lags: 12, Horizon: 1"
    )
    
    logger.add_result(result)
    logger.save_results_json('gentzkow_2019.json')
    logger.print_summary()
    
    return result


if __name__ == '__main__':
    result = run_gentzkow_replication()
