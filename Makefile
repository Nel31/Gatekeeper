# Makefile
.PHONY: install clean run-insgb run-outsgb run-all
install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run-insgb:
	. .venv/bin/activate && python cli.py \
	  --rh-file data/rh.xlsx \
	  --ext-file data/ext.xlsx \
	  --template-insgb template_insgb.xlsx \
	  --output-insgb rapport_insgb.xlsx \
	  --certificateur "Nom Prénom" \
	  --only-insgb

run-outsgb:
	. .venv/bin/activate && python cli.py \
	  --rh-file data/rh.xlsx \
	  --ext-file data/ext.xlsx \
	  --certificateur "Nom Prénom" \
	  --email-list managers.txt \
	  --use-outlook \
	  --only-outsgb

run-all:
	. .venv/bin/activate && python cli.py \
	  --rh-file data/rh.xlsx \
	  --ext-file data/ext.xlsx \
	  --template-insgb template_insgb.xlsx \
	  --output-insgb rapport_insgb.xlsx \
	  --certificateur "Nom Prénom" \
	  --email-list managers.txt \
	  --use-outlook

clean:
	rm -rf .venv __pycache__ *.pyc outsgb/ outlook_send_log.csv