# BENI LLM Annotation Guide

**Project**: Bangla Economic Narrative Index (BENI)
**Task**: LLM-assisted annotation of Bengali news articles for economic relevance and narrative content
**Primary labeler**: LLM using the fixed BENI schema
**Review scope**: Low-confidence, ambiguous, and model-disagreement cases only

---

## 1. What Is BENI?

BENI is the first Bangla-language economic narrative index — a monthly measure of economic sentiment extracted from Bengali news media. It is designed to serve as a high-frequency proxy for economic conditions in Bangladesh, where official statistics arrive with a delay and informal economic activity is large.

These 300 articles form the **LLM-labeled reference set** for BENI. The labels will be used to:
1. Measure how accurately the automated classifier detects economic content
2. Train an improved classifier using BanglaBERT (a Bengali language model)
3. Validate the narrative force and sentiment components of the index
4. Report confidence, self-consistency, and model-disagreement diagnostics

This is not a human gold-standard dataset. It is an LLM reference set with transparent validation checks.

---

## 2. Task Overview

For each article, the LLM must answer these schema fields:

| Section | Field | Type | Applies when |
|---------|-------|------|-------------|
| A | Economic relevance | Binary (Economic / Not Economic) | Always |
| A | Confidence | 1–3 stars | Always |
| A | Difficulty | Clear-cut / Borderline | Economic only |
| B | Economic topic | 12 categories | Economic only |
| C | Sentiment | Negative / Neutral / Positive | Economic only |
| D | Narrative force | 8 frames | Economic only |
| E | Valuation target | 8 actors | Economic only |
| F | Notes | Free text | Optional |

Only Section A is required for every article. Sections B–E apply only when the article is labeled "Economic."

---

## 3. Detailed Field Guide

### Section A: Economic Relevance (Required for All Articles)

**Question**: Is this article's primary subject related to Bangladesh's economy?

Select **Economic** if the article centrally addresses any of these topics in the context of Bangladesh:
- Inflation, prices, cost of living
- Exchange rates, foreign currency reserves, BDT valuation
- Monetary policy, interest rates, banking sector
- Fiscal policy, budget, taxation, government spending
- Trade, exports (especially garments), imports, tariffs
- Employment, wages, labor market
- Agriculture, food prices, food security
- Industry, manufacturing, investment, GDP growth
- Remittances, migrant workers
- Energy prices, import costs
- Economic policy or reform

Select **Not Economic** if the article's primary subject is:
- Politics (electoral campaigns, party infighting, legislative procedures) without economic framing
- Crime, accidents, law enforcement
- Sports, entertainment, culture
- General international news without Bangladesh economic implications
- Human-interest stories, celebrity news
- Weather, natural disasters (unless explicitly about economic impact)

**Important boundary cases**:

| Scenario | Decision | Rationale |
|----------|----------|-----------|
| A political speech about "rising prices hurting the poor" | **Economic** | The primary framing is economic condition, even if delivered by a politician |
| A report about a new garment factory opening | **Economic** | Directly about industry, exports, employment |
| An article about a minister being arrested for corruption | **Not Economic** | Primary subject is crime/politics, even if economic consequences exist |
| A cricket match with a sentence about sponsorship money | **Not Economic** | Primary subject is sports; economic references are incidental |
| IMF loan approval or World Bank aid package | **Economic** | Directly about fiscal/external sector economic conditions |
| Festival preparations (Eid, Pohela Boishakh) with shopping details | **Not Economic** | Primarily cultural, even if consumer spending is mentioned |

### Confidence Rating (Section A)

| Rating | Meaning | When to use |
|--------|---------|-------------|
| 1 — Guessing | You're unsure; the evidence is ambiguous | Rare — only for articles where you genuinely cannot decide |
| 2 — Fairly sure | You have moderate confidence in your decision | Default for most articles |
| 3 — Certain | The article is unambiguous; a second reader would almost certainly agree | Clear-cut cases (e.g., sports article with zero economic content, or a Bangladesh Bank policy announcement) |

### Difficulty Flag (Section A, Economic articles only)

- **Clear-cut**: The article is unambiguously economic. A second annotator would almost certainly agree.
- **Borderline**: The economic relevance is debatable. This could go either way. Flagging these helps us identify where the classifier needs improvement.

---

### Section B: Economic Topic (Choose One)

Select the SINGLE most relevant macro topic. If an article spans multiple topics, choose the one that best captures the article's central argument or headline.

| Topic | Includes | Example signal |
|-------|----------|----------------|
| Inflation & Prices | CPI, food prices, housing costs, transportation fares, general price level | "দাম বৃদ্ধি", "মূল্যস্ফীতি", "ভোক্তা মূল্য সূচক" |
| Exchange Rate & Reserves | BDT/USD rate, forex reserves, balance of payments | "ডলারের দাম", "বিনিময় হার", "রিজার্ভ" |
| Monetary Policy & Banking | Interest rates, repo rate, Bangladesh Bank decisions, banking sector stability | "সুদের হার", "বাংলাদেশ ব্যাংক", "ঋণ" |
| Fiscal Policy & Budget | National budget, taxation, subsidies, government expenditure | "বাজেট", "কর", "ভর্তুকি", "সরকারি ব্যয়" |
| Trade, Exports & External | Garments exports, imports, trade deficit, tariffs | "রপ্তানি", "আমদানি", "বাণিজ্য", "পোশাক শিল্প" |
| Employment & Wages | Jobs, unemployment, wages, labor rights | "বেকারত্ব", "শ্রমিক", "মজুরি" |
| Agriculture & Food Security | Crops, harvest, food supply, farming | "কৃষি", "ফসল", "খাদ্য নিরাপত্তা" |
| Industry, Investment & Growth | Manufacturing, FDI, GDP, infrastructure | "শিল্প", "বিনিয়োগ", "জিডিপি", "অবকাঠামো" |
| Remittances & Migration | Migrant workers, remittance inflows | "রেমিট্যান্স", "প্রবাসী আয়" |
| Energy & Import Costs | Fuel prices, electricity, LNG imports | "জ্বালানি", "বিদ্যুৎ", "তেলের দাম" |
| General Economy / Multiple | Broad economic overview, covers several topics without primary focus | "অর্থনৈতিক অবস্থা" |
| Other | Economic content not fitting above categories | — |

---

### Section C: Sentiment (Economic Articles Only)

Rate the **economic outlook** conveyed by the article — not the political sentiment, not the tone about individuals.

| Value | Meaning | Example framing |
|-------|---------|-----------------|
| Negative | The article portrays Bangladesh's economic conditions as worsening, risky, or concerning | "অর্থনীতি সংকটে", "মূল্যস্ফীতি বেড়ে যাওয়া", "রিজার্ভ কমছে" |
| Neutral / Mixed | The article reports economic conditions without strong positive or negative evaluation, or presents a balanced view | "অর্থনৈতিক প্রতিবেদন", তথ্যমূলক, বা মিশ্র মূল্যায়ন |
| Positive | The article portrays Bangladesh's economic conditions as improving, stable, or promising | "অর্থনীতি ঘুরে দাঁড়াচ্ছে", "রপ্তানি বাড়ছে", "বিনিয়োগ বাড়ছে" |

**Important**: Focus on the economic content. An article that is politically critical of the government may still be economically neutral or mixed if it reports economic data without a strong evaluative frame.

---

### Section D: Narrative Force (Economic Articles Only)

This captures HOW the article frames the economic situation — the emotional/evaluative lens beyond factual reporting.

| Frame | Meaning | Example |
|-------|---------|---------|
| Crisis / Warning | Language of emergency, imminent danger, urgent action needed | "অর্থনীতি সংকটের মুখে", "সতর্কতা", "ভয়াবহ পরিস্থিতি" |
| Burden / Hardship | Focus on suffering, difficulty, cost borne by ordinary people | "দুর্ভোগ", "বোঝা", "সাধারণ মানুষের কষ্ট" |
| Blame / Criticism | Attribution of economic problems to specific actors or policies | "দায়ী সরকার", "ব্যর্থ নীতি", "অভিযোগ" |
| Reform / Solution | Emphasis on policy changes, solutions, improvements being made | "সংস্কার", "সমাধান", "উদ্যোগ", "নতুন নীতি" |
| Stability / Confidence | Reassuring tone, emphasis on economic resilience and sound management | "স্থিতিশীল", "আস্থা", "সুশাসন" |
| Uncertainty / Concern | Ambiguous outlook, worry about future direction, lack of clarity | "অনিশ্চয়তা", "শঙ্কা", "ঝুঁকি" |
| Resilience / Opportunity | Focus on overcoming challenges, positive potential, silver linings | "সক্ষমতা", "সম্ভাবনা", "ঘুরে দাঁড়ানো" |
| Neutral Reporting | Purely descriptive, no evaluative framing, facts only | তথ্যমূলক, বিশ্লেষণাত্মক নয় |

---

### Section E: Valuation Target (Economic Articles Only)

Who or what is the article evaluating, blaming, crediting, or discussing in economic terms?

| Target | Includes |
|--------|----------|
| Government | Ministries, ministers, politicians, government policies |
| Central Bank | Bangladesh Bank, monetary authority, governor |
| Banks & Financial Institutions | Commercial banks, microfinance, non-bank financial institutions |
| Businesses & Private Sector | Companies, factory owners, private sector generally |
| Households & Consumers | General public, consumers, workers, farmers |
| Global Economy / External Actors | IMF, World Bank, foreign governments, global markets |
| Market Actors | Investors, stock market, traders |
| Unnamed / General System | No specific target; general economic conditions |

---

## 4. LLM Labeling Workflow

1. Provide the LLM with the headline, article text, source, and date when available.
2. Apply Section A first: decide Economic / Not Economic, assign confidence, and flag difficulty if Economic.
3. If Economic, fill Sections B–E: Topic → Sentiment → Narrative Force → Valuation Target.
4. Add a short note for borderline or ambiguous cases.
5. Store confidence and uncertainty flags in the output record.
6. Send low-confidence and model-disagreement cases to the review queue.

Recommended output shape:

```json
{
  "article_id": "string",
  "economic_relevance": "Economic | Not Economic",
  "confidence": 1,
  "difficulty": "Clear-cut | Borderline | null",
  "economic_topic": "string | null",
  "sentiment": "negative | neutral | positive | null",
  "narrative_force": "string | null",
  "valuation_target": "string | null",
  "uncertain": false,
  "notes": "short rationale"
}
```

---

## 5. Common Pitfalls

| Pitfall | Guidance |
|---------|----------|
| Confusing "political" with "economic" | An article about political leaders IS NOT automatically economic. Ask: is the PRIMARY subject the economy, or is the economy mentioned incidentally in a political story? |
| Reading too fast | Bengali news headlines can be misleading. Read at least the first 3–4 paragraphs before deciding. |
| Being influenced by the pre-label | Keyword or model labels are noisy baselines. The LLM decision should be based on the article text and schema. |
| Selecting "Both" when forced to choose one topic | Choose the topic that matches the article's CENTRAL argument, not every topic mentioned. |
| Letting sentiment bleed into narrative force | Sentiment = positive/negative/neutral about the economy. Narrative force = the frame (crisis vs. reform vs. uncertainty). They are related but distinct. |

---

## 6. Quality Expectations

- **Economic relevance agreement**: target high observed agreement between repeated LLM passes or across LLM/model checks.
- **Disagreement reporting**: report LLM vs TF-IDF and LLM vs BanglaBERT agreement, kappa, and class base rates.
- **Uncertainty review**: inspect low-confidence labels and cases where systems disagree.
- **Transparency**: describe these as LLM reference labels, not human gold-standard labels.

---

## 7. Ambiguous Cases

If an article genuinely does not fit the schema, or if the LLM is uncertain:
1. Make the best schema-consistent decision.
2. Set confidence to 1.
3. Mark difficulty as Borderline if the article is Economic.
4. Add a note explaining the uncertainty.
5. Set `uncertain=true` or add the article to the review queue.

Do not skip articles. Every article needs a decision, even if it is uncertain.
