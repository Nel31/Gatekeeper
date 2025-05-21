# Makefile
.PHONY: install clean run

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	. .venv/bin/activate && python cli.py \
		--rh    data/rh_reference_1.xlsx \
		--rh    data/rh_reference_2.xlsx \
		--ext   data/ext_generated.xlsx \
		--template data/template_revue.xlsx \
		--output   data/review.xlsx \
		-c "John Doe" \
		-t 120

clean:
	rm -rf .venv __pycache__ *.pyc
