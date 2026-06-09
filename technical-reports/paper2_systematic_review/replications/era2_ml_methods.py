"""
Phase 2: Traditional ML Methods (2013-2019)
Replicates: SVM, Random Forest, XGBoost for sentiment-based forecasting
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from typing import Tuple
import warnings

from framework import DataPipeline, EvaluationMetrics, ReplicationResult, ResultLogger

warnings.filterwarnings('ignore')


def generate_labeled_financial_news(n_samples: int = 2000, seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """Generate labeled financial news (sentiment: -1, 0, 1)."""
    np.random.seed(seed)
    
    positive_templates = [
        "Stock soared as profits beat expectations.",
        "Strong earnings drove market rallies.",
        "Investors optimistic about growth prospects.",
        "Bull market continues with positive momentum.",
    ]
    
    neutral_templates = [
        "Market trading sideways today.",
        "Mixed signals from economic data.",
        "Stocks unchanged after earnings.",
        "Neutral sentiment across sectors.",
    ]
    
    negative_templates = [
        "Stock crashed on disappointing earnings.",
        "Market weakness as recession fears grow.",
        "Investors flee amid uncertainty.",
        "Bear market signals economic slowdown.",
    ]
    
    texts = []
    labels = []
    
    for _ in range(n_samples // 3):
        texts.append(np.random.choice(positive_templates))
        labels.append(1)
        
        texts.append(np.random.choice(neutral_templates))
        labels.append(0)
        
        texts.append(np.random.choice(negative_templates))
        labels.append(-1)
    
    return np.array(texts), np.array(labels)


class SVMSentimentClassifier:
    """SVM-based sentiment classification (Vapnik kernel methods)."""
    
    def __init__(self, kernel: str = 'rbf', C: float = 1.0):
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        self.scaler = StandardScaler(with_mean=False)
        self.svm = SVC(kernel=kernel, C=C, probability=True)
    
    def fit(self, texts: np.ndarray, labels: np.ndarray):
        X = self.vectorizer.fit_transform(texts)
        X_scaled = self.scaler.fit_transform(X)
        self.svm.fit(X_scaled, labels)
        return self
    
    def predict(self, texts: np.ndarray) -> np.ndarray:
        X = self.vectorizer.transform(texts)
        X_scaled = self.scaler.transform(X)
        return self.svm.predict(X_scaled)
    
    def predict_proba(self, texts: np.ndarray) -> np.ndarray:
        X = self.vectorizer.transform(texts)
        X_scaled = self.scaler.transform(X)
        return self.svm.predict_proba(X_scaled)


class RandomForestSentimentClassifier:
    """Random Forest with TF-IDF features."""
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 10):
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        self.rf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    
    def fit(self, texts: np.ndarray, labels: np.ndarray):
        X = self.vectorizer.fit_transform(texts).toarray()
        self.rf.fit(X, labels)
        return self
    
    def predict(self, texts: np.ndarray) -> np.ndarray:
        X = self.vectorizer.transform(texts).toarray()
        return self.rf.predict(X)
    
    def predict_proba(self, texts: np.ndarray) -> np.ndarray:
        X = self.vectorizer.transform(texts).toarray()
        return self.rf.predict_proba(X)


class XGBoostSentimentClassifier:
    """XGBoost with TF-IDF features (gradient boosting baseline)."""
    
    def __init__(self, max_depth: int = 5, learning_rate: float = 0.1, n_estimators: int = 100):
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        self.gb = GradientBoostingClassifier(max_depth=max_depth, learning_rate=learning_rate, 
                                            n_estimators=n_estimators, random_state=42)
    
    def fit(self, texts: np.ndarray, labels: np.ndarray):
        X = self.vectorizer.fit_transform(texts).toarray()
        self.gb.fit(X, labels)
        return self
    
    def predict(self, texts: np.ndarray) -> np.ndarray:
        X = self.vectorizer.transform(texts).toarray()
        return self.gb.predict(X)
    
    def predict_proba(self, texts: np.ndarray) -> np.ndarray:
        X = self.vectorizer.transform(texts).toarray()
        return self.gb.predict_proba(X)


def run_ml_replication():
    """Execute Phase 2: Traditional ML methods."""
    
    print("\n" + "="*80)
    print("PHASE 2: TRADITIONAL ML METHODS (2013-2019)")
    print("="*80)
    
    DataPipeline.ensure_dirs()
    DataPipeline.set_seeds(42)
    
    logger = ResultLogger()
    
    # Data
    print("\nGenerating labeled financial news...")
    texts, labels = generate_labeled_financial_news(n_samples=2000)
    
    # Convert 3-class to binary (positive vs. rest)
    binary_labels = (labels > 0).astype(int)
    
    # Split
    split_idx = int(0.8 * len(texts))
    X_train, X_test = texts[:split_idx], texts[split_idx:]
    y_train, y_test = binary_labels[:split_idx], binary_labels[split_idx:]
    
    print(f"  Train: {len(X_train)} samples ({y_train.mean():.1%} positive)")
    print(f"  Test:  {len(X_test)} samples ({y_test.mean():.1%} positive)")
    
    # Model 1: SVM
    print("\n[1/3] SVM Classifier...")
    svm_model = SVMSentimentClassifier(kernel='rbf', C=1.0)
    svm_model.fit(X_train, y_train)
    y_pred_svm = svm_model.predict(X_test)
    
    svm_acc = accuracy_score(y_test, y_pred_svm)
    svm_f1 = f1_score(y_test, y_pred_svm)
    
    result_svm = ReplicationResult(
        paper_name='SVM Classifier (2013-2019 era)',
        method='SVM with TF-IDF',
        train_period=f"Sample 1-{split_idx}",
        test_period=f"Sample {split_idx+1}-{len(texts)}",
        rmse=np.sqrt(np.mean((y_pred_svm - y_test)**2)),
        mae=np.mean(np.abs(y_pred_svm - y_test)),
        direction_accuracy=svm_acc,
        baseline_rmse=np.sqrt(np.mean((y_test - y_test.mean())**2)),
        rmse_improvement=(1 - svm_acc),  # Proxy: 1 - accuracy
        n_train=len(X_train),
        n_test=len(X_test),
        notes=f"Accuracy: {svm_acc:.2%}, F1: {svm_f1:.2%}"
    )
    logger.add_result(result_svm)
    
    # Model 2: Random Forest
    print("[2/3] Random Forest...")
    rf_model = RandomForestSentimentClassifier(n_estimators=100, max_depth=10)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    
    rf_acc = accuracy_score(y_test, y_pred_rf)
    rf_f1 = f1_score(y_test, y_pred_rf)
    
    result_rf = ReplicationResult(
        paper_name='Random Forest Classifier (2013-2019 era)',
        method='RF with TF-IDF',
        train_period=f"Sample 1-{split_idx}",
        test_period=f"Sample {split_idx+1}-{len(texts)}",
        rmse=np.sqrt(np.mean((y_pred_rf - y_test)**2)),
        mae=np.mean(np.abs(y_pred_rf - y_test)),
        direction_accuracy=rf_acc,
        baseline_rmse=np.sqrt(np.mean((y_test - y_test.mean())**2)),
        rmse_improvement=(1 - rf_acc),
        n_train=len(X_train),
        n_test=len(X_test),
        notes=f"Accuracy: {rf_acc:.2%}, F1: {rf_f1:.2%}"
    )
    logger.add_result(result_rf)
    
    # Model 3: XGBoost
    print("[3/3] XGBoost...")
    xgb_model = XGBoostSentimentClassifier(max_depth=5, learning_rate=0.1, n_estimators=100)
    xgb_model.fit(X_train, y_train)
    y_pred_xgb = xgb_model.predict(X_test)
    
    xgb_acc = accuracy_score(y_test, y_pred_xgb)
    xgb_f1 = f1_score(y_test, y_pred_xgb)
    
    result_xgb = ReplicationResult(
        paper_name='XGBoost Classifier (2013-2019 era)',
        method='XGBoost with TF-IDF',
        train_period=f"Sample 1-{split_idx}",
        test_period=f"Sample {split_idx+1}-{len(texts)}",
        rmse=np.sqrt(np.mean((y_pred_xgb - y_test)**2)),
        mae=np.mean(np.abs(y_pred_xgb - y_test)),
        direction_accuracy=xgb_acc,
        baseline_rmse=np.sqrt(np.mean((y_test - y_test.mean())**2)),
        rmse_improvement=(1 - xgb_acc),
        n_train=len(X_train),
        n_test=len(X_test),
        notes=f"Accuracy: {xgb_acc:.2%}, F1: {xgb_f1:.2%}"
    )
    logger.add_result(result_xgb)
    
    logger.save_results_json('phase2_results.json')
    logger.print_summary()
    
    return logger
