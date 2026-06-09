# Linguistic Data Contributions

This directory contains templates and submissions for native-language data contributed by linguistic experts.

## Templates

| File | Purpose |
|------|---------|
| `text_submission_template.csv` | Submit native-language news articles or text data |
| `annotation_template.csv` | Label articles as Economic / Not Economic with cultural context |
| `dialect_template.csv` | Document dialectal variants, idioms, and culturally specific expressions |
| `metadata_form.csv` | Provide language metadata (name, speakers, region, license) |

## Submissions

Submitted data goes in `submissions/`. Each submission should include:
1. A metadata form (use `metadata_form.csv`)
2. The text data file(s) (use `text_submission_template.csv`)
3. Annotations if available (use `annotation_template.csv`)
4. The contributor's row in `../OWNERS.csv`

## Process

1. Download the relevant template
2. Fill with your data
3. Open a pull request or email to lila.lab0x@gmail.com
4. We verify format, record your contribution in `OWNERS.csv`, and run the pipeline

## Licensing

Default license for contributed data: **CC BY 4.0** (you may choose a different license).
You retain ownership. You license the project to use your data for research and publication.
