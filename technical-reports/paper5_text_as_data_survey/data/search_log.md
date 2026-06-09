# Paper 5 Search Log

Status: preliminary candidate search, not final systematic screening.

Date run: 2026-06-07

## Web Search Sources

Manual web search was used to identify known anchor works and recent LLM-era papers. Sources included publisher pages, Cambridge Core, Springer, MIT Press, SSRN, arXiv pages, Hugging Face paper pages, and Crossref metadata.

Examples identified through web search include:

- Grimmer and Stewart, "Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts."
- Gentzkow, Kelly, and Taddy, "Text as Data."
- Grimmer, Roberts, and Stewart, *Text as Data: A New Framework for Machine Learning and the Social Sciences*.
- Roberts et al., "Structural Topic Models for Open-Ended Survey Responses."
- Ziems et al., "Can Large Language Models Transform Computational Social Science?"
- Gilardi et al., "ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks."
- Argyle et al., "Out of One, Many: Using Language Models to Simulate Human Samples."
- Bisbee et al., "Synthetic Replacements for Human Survey Data? The Perils of Large Language Models."
- Tornberg, "Large Language Models Outperform Expert Coders and Supervised Classifiers at Annotating Political Social Media Messages."

## Crossref Search

The script `scripts/search_crossref_candidates.py` queried Crossref using these search strings:

- `text as data social science`
- `automated text analysis social science`
- `content analysis social sciences methodology`
- `computational text analysis political science`
- `text as data economics`
- `news sentiment economics text as data`
- `economic policy uncertainty newspaper text`
- `topic models social science`
- `structural topic model social science`
- `machine learning text political science`
- `LIWC psychology text analysis`
- `large language models computational social science`
- `ChatGPT text annotation social science`
- `large language models political science`
- `large language models qualitative analysis social science`
- `multilingual text analysis social science`

Command:

```bash
python3 technical-reports/paper5_text_as_data_survey/scripts/search_crossref_candidates.py --rows 40
```

Output:

- `data/crossref_candidate_papers.csv`

Result:

- 301 candidate records.

## Screening Queue

The script `scripts/screen_crossref_candidates.py` ranks candidates for human screening.

Command:

```bash
python3 technical-reports/paper5_text_as_data_survey/scripts/screen_crossref_candidates.py
```

Output:

- `data/crossref_screening_queue.csv`

## Important Limitations

- Crossref search is metadata-based and noisy.
- Candidate records are not included papers.
- Human screening is still required.
- Web of Science, Scopus, JSTOR, SSRN, and arXiv searches still need formal export when access is available.
- The final review should record exclusion reasons and produce a PRISMA flow diagram.

## PDF Download Attempt

Only open/direct PDFs were downloaded. Paywalled or access-controlled publisher files were not bypassed.

Commands:

```bash
python3 technical-reports/paper5_text_as_data_survey/scripts/download_candidate_pdfs.py --priority screen_first
python3 technical-reports/paper5_text_as_data_survey/scripts/download_candidate_pdfs.py --priority all --manifest technical-reports/paper5_text_as_data_survey/literature/download_manifest_all.csv
```

The `screen_first` pass completed and wrote:

- `literature/download_manifest.csv`

The full `all` pass was stopped because it was taking too long across publisher endpoints. It downloaded additional open PDFs before interruption, but did not complete a full manifest. The actual local PDF list is recorded in:

- `literature/local_pdf_inventory.csv`

Current local PDF count: 13.
