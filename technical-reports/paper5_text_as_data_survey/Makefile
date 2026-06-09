.PHONY: assets pdf

assets:
	python3 scripts/build_review_assets.py

pdf: assets
	cd manuscript && pdflatex -interaction=nonstopmode paper5_text_as_data_survey.tex && pdflatex -interaction=nonstopmode paper5_text_as_data_survey.tex
