╔═══════════════════════════════════════════════════════════════════╗
║           README: arXiv PREPRINT PREPARATION FOLDER              ║
║   Economic Narrative Indices: A Systematic Review (2007--2025)   ║
╚═══════════════════════════════════════════════════════════════════╝

AUTHOR:
  Ann Naser Nabil
  Department of Economics, Jahangirnagar University
  Savar, Dhaka 1342, Bangladesh
  Email: ann.n.nabil@gmail.com
  ORCID: 0000-0001-8794-1065

─── STATUS ──────────────────────────────────────────────────────────
  ✓ LaTeX source arXiv-ready (compiled: 29 pages, 0 errors)
  ✓ Author info embedded (not blind)
  ✓ arXiv metadata header added
  ✓ TikZ figures inline (no external image dependencies)
  ✓ All supplementary materials included

─── FOLDER CONTENTS ─────────────────────────────────────────────────

  FILE                           DESCRIPTION
  ──────────────────────────────────────────────────────────────────
  systematic_review_66papers.tex  Main LaTeX manuscript (arXiv-ready)
  refs.bib                        BibTeX bibliography
  systematic_review_66papers.pdf  Compiled preview (29 pp, ~9,000 words)

  Figures/
    figure1_timeline.pdf          Methodological evolution timeline
    figure1_timeline.tex          TikZ source for Figure 1
    figure2_performance_distribution.pdf  Box plots by domain
    figure2_performance_distribution.tex  TikZ source for Figure 2
    figure3_geographic_distribution.pdf   Geographic bar chart
    figure3_geographic_distribution.tex   TikZ source for Figure 3

  Supplementary/
    funnel_plot_publication_bias.pdf
    literature_matrix.xlsx        Complete metadata for all 66 papers
    papers_database.csv           Raw paper database
    quality_assessment.xlsx       Risk-of-bias scores
    results_data_raw.csv          Raw synthesis data
    README.txt                    Notes on supplementary files

─── arXiv SUBMISSION CHECKLIST ──────────────────────────────────────

  [ ] 1. REGISTER/LOGIN at https://arxiv.org/login
  [ ] 2. START NEW SUBMISSION
  [ ] 3. SELECT CATEGORIES:
         Primary:   econ.EM (Econometrics)
         Secondary: q-fin.ST (Statistical Finance),
                    cs.CL   (Computation and Language)
  [ ] 4. ENTER METADATA:
         Title: Economic Narrative Indices and Media-Based Sentiment
                Measures: A Systematic Review of Methodologies,
                Applications, and Research Gaps (2007--2025)
         Authors: Ann Naser Nabil
         Abstract: (copy from PDF or tex file)
         Comments: 29 pages, 4 figures, 4 tables;
                   Accepted at Journal of Economic Surveys (2025)
  [ ] 5. SELECT LICENSE: arXiv.org perpetual, non-exclusive license
         (or CC BY 4.0 if preferred)
  [ ] 6. UPLOAD FILES (PACKAGE AS .tar.gz OR .zip):
         Include ALL of:
         - systematic_review_66papers.tex  (main file)
         - refs.bib                         (bibliography)
         - Figures/*.pdf                    (figure PDFs)
         - Figures/*.tex                    (figure sources)
         - Supplementary/                   (optional, for ancillary)

         IMPORTANT: arXiv compiles with PDFLaTeX by default.
         The source is tested and compatible.

  [ ] 7. PROCESSING: arXiv will auto-compile. Check the PDF
         preview before confirming. If TikZ is slow, arXiv allows
         submitting a precompiled PDF instead.

  [ ] 8. PREVIEW & CONFIRM submission.

─── KEY DIFFERENCES FROM JES SUBMISSION ─────────────────────────────

  JES Submission                    arXiv Version
  ────────────────────────────────  ─────────────────────────────────
  Blind review (no author info)     Author name + affiliation visible
  JES-specific formatting           Standard article class
  JEL codes only                    JEL codes + arXiv categories
  No license specified              CC BY 4.0 / arXiv license
  Separate title page file          Title in main PDF
  Cover letter & checklist          Not included (arXiv only needs
                                    source files)

─── arXiv COMPATIBILITY NOTES ───────────────────────────────────────

  - Uses standard 'article' document class — fully arXiv-compatible
  - TikZ/pgfplots are inline and will render on arXiv's TeX Live
  - If TikZ compilation times out on arXiv (rare for this size),
    submit the pre-compiled systematic_review_66papers.pdf instead
  - All fonts are standard (T1 encoding, Computer Modern)
  - No external packages beyond TeX Live base
  - Hyperref configured with hypertexnames=false for arXiv safety

─── CONTACT ─────────────────────────────────────────────────────────

  Ann Naser Nabil
  Email: ann.n.nabil@gmail.com
  ORCID: 0000-0001-8794-1065

  Prepared: June 5, 2026
