isort:
	isort -rc

black:
	black .

lint: isort black

lintcommit:
	git commit -m "🕶 format code" --author="Lint Bot <stefan+lint-bot@foulis.ch>"
