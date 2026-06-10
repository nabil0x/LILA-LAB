# LILA Lab Glossary

> The lexicon of the LILA Lab project. Terms are listed alphabetically. If you are new to the project, start with **BENI**, **XENI**, and **narrative index**.

---

## A

**Adjudication**
The process of resolving disagreements between multiple LLM annotators (or between LLM and human annotators) on the same article. In the BENI pipeline, adjudication uses majority voting across a Claude/GPT-4o ensemble, with tiebreakers going to the higher-confidence label. The adjudicated labels become the ground truth for classifier training. See [`pipelines/beni/annotation/ADJUDICATION_PROTOCOL.md`](pipelines/beni/annotation/ADJUDICATION_PROTOCOL.md).

**AENI (Assamese Exploration & Native-language Intelligence)**
The planned XENI pipeline for Assamese (অসমীয়া), spoken by approximately 15 million people. AENI follows the same structure as BENI but targets Assamese-language news sources. The pipeline is in early development and seeking contributors. See [AENI pipeline](pipelines/aeni/).

**Annotation schema**
The structured set of fields and labels used to classify each news article. The current BENI schema uses a binary economic relevance label (Economic / Not Economic) with confidence and difficulty flags. A planned Phase 2 expansion adds fields for economic topic, narrative force, valuation target, and sentiment polarity. See [`pipelines/beni/annotation/ANNOTATION_SCHEMA.md`](pipelines/beni/annotation/ANNOTATION_SCHEMA.md).

---

## B

**BanglaBERT**
A pre-trained Bangla language model (`csebuetnlp/banglabert`) based on the Electra architecture (424 MB). It serves as the deep-learning classifier alongside the TF-IDF baseline in the BENI pipeline. Full fine-tuning on the full 70,000-article training set is scheduled for a Kaggle GPU run. See [`pipelines/beni/experiment/beni_pilot/banglabert.py`](pipelines/beni/experiment/beni_pilot/banglabert.py).

**BENI (Bangla Exploration & Native-language Intelligence)**
The first proven XENI pipeline, built for the Bangla language (265 million speakers). BENI collects Bangla news articles from six major Bangladeshi newspapers, annotates them for economic relevance using an LLM ensemble (Claude, GPT-4o), trains a classifier (TF-IDF + logistic regression at 91.7% accuracy), constructs a monthly narrative index, and validates it against macroeconomic indicators. BENI is the flagship pipeline of LILA Lab. See [`pipelines/beni/`](pipelines/beni/).

**BENI Economic Index**
The monthly narrative index produced by the BENI pipeline. It measures the share of economic news in Bangla-language media over time. The index spans 79 months (June 2014 to December 2020), shows a mean economic news share of 38.9%, and correlates strongly with CPI (r = -0.75) and the BDT/USD exchange rate (r = -0.72) at the level. The index is built by aggregating article-level classifier predictions into monthly proportions.

**BENI Pilot**
The first end-to-end experimental run of the BENI pipeline, from raw Potrika news CSVs to a validated monthly narrative index. The pilot proved the pipeline concept using a TF-IDF + logistic regression classifier and established the 79-month baseline index. It is the runnable reference implementation documented in [`pipelines/beni/experiment/beni_pilot/`](pipelines/beni/experiment/beni_pilot/).

---

## C

**CENI (Chittagonian Exploration & Native-language Intelligence)**
The planned XENI pipeline for Chittagonian (চাঁটগাঁইয়া), a dialect of Bangla spoken by approximately 16 million people in the Chittagong region of Bangladesh. Currently in the planning stage and seeking contributors.

---

## L

**LLM annotation**
The use of large language models (Claude, GPT-4o) to label news articles according to the annotation schema. LLM annotation replaces or augments human annotation for scalability. The BENI pipeline runs each article through multiple LLMs and adjudicates the results. See [`pipelines/beni/annotation/llm_annotate.py`](pipelines/beni/annotation/llm_annotate.py).

**LLM ensemble**
A collection of multiple LLMs (currently Claude and GPT-4o) that each annotate the same article independently. Their labels are combined through adjudication (majority voting) to produce a consensus label. Ensembling improves annotation reliability and provides confidence estimates.

**Locked reference set**
See **reference set**.

---

## M

**Macroeconomic validation**
The process of comparing the BENI narrative index against real-world macroeconomic indicators (CPI inflation, exchange rates, foreign exchange reserves). Strong correlations support the claim that the narrative index captures economically meaningful signal. In the BENI pilot, level correlations reached r = -0.75 with CPI and r = -0.72 with the exchange rate, both statistically significant at p < 0.001.

---

## N

**Narrative force / narrative regime**
Narrative force refers to the intensity or pressure conveyed by economic discourse in news articles. A narrative regime is a sustained period in which a particular narrative pattern dominates (for example, a sustained focus on inflation versus trade). These are planned extensions to the BENI pipeline, tracked through fields like `narrative_force` (crisis, burden, blame, reform, stability, uncertainty, resilience, neutral) and analyzed via topic modeling. See [`pipelines/beni/experiment/beni_pilot/narrative.py`](pipelines/beni/experiment/beni_pilot/narrative.py).

**Narrative index**
A monthly time series that measures the prevalence of a particular narrative (for example, economic news) in a language's media ecosystem. It is constructed by classifying each article in a corpus, aggregating the classifications by month, and computing the proportion of articles that belong to the target narrative class. The BENI Economic Index is the lab's first proven narrative index, built from 120,707 articles across 79 months.

**NENI (Nepali Exploration & Native-language Intelligence)**
The planned XENI pipeline for Nepali (नेपाली), spoken by approximately 25 million people. In early planning and seeking contributors.

---

## P

**Potrika corpus / dataset**
A Bangla news corpus published on Mendeley Data (DOI: 10.17632/v362rp78dc.4, CC BY 4.0). It contains 664,880 articles from six major Bangladeshi newspapers (Jugantor, Ittefaq, Kaler Kontho, Inqilab, Jaijaidin, Somoyer Alo) spanning 2014 to 2020. The corpus is organized into 39 CSV files (3.3 GB) with categories including Economy, National, Politics, Worldnews, Sports, Education, Entertainment, and Science & Technology. It is the primary data source for the BENI pipeline.

**Potrika Timeseries**
A processed subset of the Potrika corpus used for training and evaluating the BENI classifier. It combines Economy articles (positive class, approximately 38,000) with sampled National, Politics, and Worldnews articles (negative class, approximately 82,000), preserving publication dates for time-series-aware train/val/test splits. The full timeseries contains 120,707 articles.

---

## R

**Reference set / locked reference set**
A curated, human-validated subset of annotated articles that serves as the gold standard for classifier evaluation. Once the reference set is locked, no further changes are made to its labels, ensuring that all future model comparisons use the same evaluation ground truth. The BENI pipeline is building a 300-article locked reference set.

---

## S

**SENI (Sylheti Exploration & Native-language Intelligence)**
The planned XENI pipeline for Sylheti (চিটাঙ্গ / ꠍꠤꠟꠐꠤ), spoken by approximately 11 million people. Currently in the planning stage and seeking contributors.

---

## T

**TF-IDF baseline**
The baseline classifier used in the BENI pipeline: a TF-IDF vectorizer (80,000 max features, unigram + bigram) paired with a logistic regression classifier (one-vs-rest, balanced class weights). It achieves 91.7% accuracy and 0.894 macro F1 on the economic relevance task. This baseline serves as the reference point for evaluating more complex models like BanglaBERT.

---

## X

**XENI ([Language initial] + Exploration & Native-language Intelligence)**
The naming convention for LILA Lab's NLP pipelines. Each pipeline is named by taking the first letter of the target language and appending "ENI" (Exploration & Native-language Intelligence). Examples: BENI (Bangla), AENI (Assamese), NENI (Nepali), SENI (Sylheti), CENI (Chittagonian). Every XENI pipeline follows the same structure: news collection, LLM annotation, classifier training, index construction, and macroeconomic validation. See [`pipelines/README.md`](pipelines/README.md).
