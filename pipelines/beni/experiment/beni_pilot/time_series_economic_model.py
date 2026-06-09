"""
Time-Series Economic Narrative Model
Tracks economic variable similarity over time to detect socio-economic trends.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


class EconomicVariableEncoder:
    """Encode economic keywords into a time-varying similarity matrix."""
    
    ECONOMIC_VARIABLES = {
        "monetary": ["ব্যাংক", "সুদ", "টাকা", "আর্থিক", "রিজার্ভ"],
        "inflation": ["মূল্যস্ফীতি", "দাম", "ক্রয়ক্ষমতা", "মূল্য"],
        "trade": ["রপ্তানি", "আমদানি", "বাণিজ্য", "টেরিফ"],
        "growth": ["জিডিপি", "বৃদ্ধি", "উৎপাদন", "শিল্প", "বিনিয়োগ"],
        "employment": ["কর্মসংস্থান", "বেকারত্ব", "মজুরি", "কাজ"],
        "fiscal": ["কর", "বাজেট", "রাজস্ব", "ঋণ", "সরকারি"],
    }
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.domains = list(self.ECONOMIC_VARIABLES.keys())
    
    def text_to_domain_vector(self, text: str) -> np.ndarray:
        """Convert text to 6-dim economic domain vector (keyword counts)."""
        text_lower = text.lower()
        vector = np.zeros(len(self.domains))
        
        for idx, domain in enumerate(self.domains):
            for keyword in self.ECONOMIC_VARIABLES[domain]:
                vector[idx] += text_lower.count(keyword.lower())
        
        return vector
    
    def compute_domain_similarity(self, vector: np.ndarray) -> np.ndarray:
        """Compute pairwise cosine similarity between domains."""
        if vector.sum() == 0:
            return np.eye(len(self.domains))
        
        # Reshape to column vectors for cosine_similarity
        vectors = vector.reshape(-1, 1)
        sim = cosine_similarity(vectors.T).flatten()
        
        # Expand to full domain x domain similarity matrix
        domain_sim = np.outer(vector, vector)
        domain_sim /= (np.linalg.norm(vector) ** 2 + 1e-8)
        
        return domain_sim


class TemporalEconomicNarrative:
    """Model economic narrative evolution over time."""
    
    def __init__(self, articles_df: pd.DataFrame):
        """
        Args:
            articles_df: DataFrame with columns ['date', 'text', 'class_label', 'economic_relevance']
        """
        self.articles_df = articles_df.copy()
        self.encoder = EconomicVariableEncoder()
        self.time_series = None
        self.domain_trends = None
    
    def fit(self, freq: str = "W") -> TemporalEconomicNarrative:
        """
        Aggregate articles by time period and compute domain statistics.
        
        Args:
            freq: Pandas frequency ('D' for daily, 'W' for weekly, 'M' for monthly)
        """
        # Ensure date column exists
        if 'date' not in self.articles_df.columns:
            raise ValueError("DataFrame must have 'date' column")
        
        self.articles_df['date'] = pd.to_datetime(self.articles_df['date'])
        
        # Encode all articles
        self.articles_df['econ_vector'] = self.articles_df['text'].apply(
            self.encoder.text_to_domain_vector
        )
        
        # Aggregate by time period
        time_groups = self.articles_df.groupby(pd.Grouper(key='date', freq=freq))
        
        results = []
        for period, group in time_groups:
            if len(group) == 0:
                continue
            
            # Mean domain activation
            domain_means = np.mean(np.array(group['econ_vector'].tolist()), axis=0)
            
            # Economic article ratio
            econ_ratio = group['economic_relevance'].mean() if 'economic_relevance' in group.columns else 0
            
            # Most activated domain
            top_domain = self.encoder.domains[np.argmax(domain_means)]
            
            results.append({
                'period': period,
                'n_articles': len(group),
                'n_economic': group['economic_relevance'].sum() if 'economic_relevance' in group.columns else 0,
                'econ_ratio': econ_ratio,
                **{f'domain_{d}': domain_means[i] for i, d in enumerate(self.encoder.domains)},
                'top_domain': top_domain,
            })
        
        self.time_series = pd.DataFrame(results).set_index('period')
        return self
    
    def domain_similarity_over_time(self) -> pd.DataFrame:
        """Compute cosine similarity between domain trends over time."""
        domain_cols = [c for c in self.time_series.columns if c.startswith('domain_')]
        domain_data = self.time_series[domain_cols].values  # (T, 6)
        
        # Similarity matrix: domain x domain
        domain_data_normalized = domain_data / (np.linalg.norm(domain_data, axis=1, keepdims=True) + 1e-8)
        similarity = cosine_similarity(domain_data_normalized.T)  # (6, 6)
        
        return pd.DataFrame(
            similarity,
            index=self.encoder.domains,
            columns=self.encoder.domains
        )
    
    def detect_narrative_shifts(self, window: int = 4) -> pd.DataFrame:
        """Detect significant shifts in economic narrative (rolling change detection)."""
        domain_cols = [c for c in self.time_series.columns if c.startswith('domain_')]
        domain_data = self.time_series[domain_cols].values
        
        shifts = []
        for i in range(window, len(domain_data)):
            prev_mean = domain_data[i-window:i].mean(axis=0)
            curr_val = domain_data[i]
            change = np.linalg.norm(curr_val - prev_mean)
            
            shifts.append({
                'period': self.time_series.index[i],
                'narrative_shift_magnitude': change,
                'prev_top_domain': self.encoder.domains[np.argmax(prev_mean)],
                'curr_top_domain': self.encoder.domains[np.argmax(curr_val)],
            })
        
        return pd.DataFrame(shifts).set_index('period')
    
    def get_time_series(self) -> pd.DataFrame:
        """Return aggregated time series."""
        return self.time_series


def create_synthetic_temporal_data(n_weeks: int = 26) -> pd.DataFrame:
    """Generate synthetic date-stamped articles for testing."""
    np.random.seed(42)
    
    base_date = datetime(2025, 1, 1)
    articles = []
    
    for week in range(n_weeks):
        date = base_date + timedelta(weeks=week)
        
        # Simulate 5-15 articles per week
        n_articles = np.random.randint(5, 15)
        
        for _ in range(n_articles):
            # Simulate topic distribution: more national/state in week 10-15 (elections)
            if 10 <= week <= 15:
                topic = np.random.choice(['national', 'state'], p=[0.6, 0.4])
            else:
                topic = np.random.choice(['national', 'state', 'sports', 'entertainment'], p=[0.3, 0.3, 0.2, 0.2])
            
            # Economic relevance: 3% baseline, 8% during political events
            econ_prob = 0.08 if 10 <= week <= 15 else 0.03
            is_economic = np.random.rand() < econ_prob
            
            # Generate text with economic keywords based on topic and week
            text_parts = []
            
            if is_economic:
                # Vary narrative by week (simulate trends)
                if week < 10:
                    # Monetary focus early
                    text_parts.extend(["ব্যাংক", "সুদ", "টাকা"])
                elif week < 18:
                    # Trade focus mid-period
                    text_parts.extend(["রপ্তানি", "আমদানি", "বাণিজ্য"])
                else:
                    # Growth focus late
                    text_parts.extend(["জিডিপি", "বৃদ্ধি", "বিনিয়োগ"])
            
            text_parts.append(topic)
            text = " ".join(text_parts * np.random.randint(2, 5))
            
            articles.append({
                'date': date,
                'text': text,
                'class_label': topic,
                'economic_relevance': 1 if is_economic else 0,
            })
    
    return pd.DataFrame(articles)


def compare_models() -> Dict:
    """Compare different approaches to time-series economic narrative modeling."""
    
    print("=" * 70)
    print("ECONOMIC NARRATIVE TIME-SERIES MODEL COMPARISON")
    print("=" * 70)
    
    # Generate synthetic data
    df = create_synthetic_temporal_data(n_weeks=26)
    print(f"\n✓ Generated {len(df)} synthetic articles over 26 weeks")
    print(f"  Economic articles: {df['economic_relevance'].sum()} ({df['economic_relevance'].mean()*100:.1f}%)")
    
    # Model 1: Weekly aggregation
    print("\n" + "-" * 70)
    print("MODEL 1: Weekly Domain Aggregation (Baseline)")
    print("-" * 70)
    
    model1 = TemporalEconomicNarrative(df).fit(freq='W')
    ts1 = model1.get_time_series()
    print(f"Time periods: {len(ts1)}")
    print(f"\nFirst 3 weeks:")
    print(ts1[['n_articles', 'n_economic', 'top_domain']].head(3))
    
    sim1 = model1.domain_similarity_over_time()
    print(f"\nDomain similarity matrix (weekly):")
    print(sim1.round(2))
    
    # Model 2: Bi-weekly aggregation (smoother)
    print("\n" + "-" * 70)
    print("MODEL 2: Bi-Weekly Aggregation (Smoother)")
    print("-" * 70)
    
    model2 = TemporalEconomicNarrative(df).fit(freq='2W')
    ts2 = model2.get_time_series()
    print(f"Time periods: {len(ts2)}")
    
    sim2 = model2.domain_similarity_over_time()
    print(f"Domain similarity matrix (bi-weekly):")
    print(sim2.round(2))
    
    # Model 3: Narrative shift detection
    print("\n" + "-" * 70)
    print("MODEL 3: Narrative Shift Detection (Window=4 weeks)")
    print("-" * 70)
    
    shifts = model1.detect_narrative_shifts(window=4)
    significant_shifts = shifts[shifts['narrative_shift_magnitude'] > shifts['narrative_shift_magnitude'].quantile(0.75)]
    print(f"Detected {len(significant_shifts)} significant shifts:")
    print(significant_shifts[['narrative_shift_magnitude', 'prev_top_domain', 'curr_top_domain']].tail(3))
    
    # Comparison
    print("\n" + "=" * 70)
    print("MODEL RECOMMENDATIONS")
    print("=" * 70)
    
    recommendations = {
        "MODEL_1_WEEKLY": {
            "pros": ["High temporal resolution", "Captures weekly fluctuations"],
            "cons": ["Noise from low article counts", "Overfitting to weekly variation"],
            "best_for": "Real-time monitoring with >100 articles/week",
        },
        "MODEL_2_BIWEEKLY": {
            "pros": ["Smoother trends", "Reduces noise", "Balanced resolution"],
            "cons": ["Slower to detect short-term shifts"],
            "best_for": "Policy tracking over quarters, Bangladesh news (~40-50 articles/week)",
        },
        "MODEL_3_SHIFT_DETECTION": {
            "pros": ["Identifies discrete changes", "Interpretable events"],
            "cons": ["Misses gradual trends"],
            "best_for": "Election cycles, policy announcements",
        },
    }
    
    for model_name, details in recommendations.items():
        print(f"\n{model_name}:")
        for key, val in details.items():
            if isinstance(val, list):
                print(f"  {key}: {', '.join(val)}")
            else:
                print(f"  {key}: {val}")
    
    return {
        "models": {"weekly": model1, "biweekly": model2},
        "time_series": {"weekly": ts1, "biweekly": ts2},
        "shifts": shifts,
    }


if __name__ == "__main__":
    results = compare_models()
    
    print("\n" + "=" * 70)
    print("RECOMMENDATION FOR BENGALI ECONOMIC NARRATIVES")
    print("=" * 70)
    print("""
For Bangladesh economic news:
1. Use BI-WEEKLY aggregation (MODEL 2)
   - Typical economic articles: 40-50/week
   - Bi-weekly (80-100 articles) balances noise vs. resolution
   - Aligns with policy cycles (RBI/BB statements, budget announcements)

2. Combine with shift detection (MODEL 3)
   - Detect when narrative focus changes (e.g., monetary → trade)
   - Flag periods with >1.5σ narrative shift
   - Correlate shifts with policy events

3. Add sentiment layer
   - Per domain: % negative articles
   - Track if monetary policy sentiment shifts from neutral → negative
   - This reveals "narrative pressure"

4. Ensemble: Time-series + Transformer
   - Time-series: captures aggregate domain trends (interpretable)
   - Transformer (BanglaBERT): captures semantic narrative shifts (realistic)
   - Cross-validate predictions for robustness
    """)
