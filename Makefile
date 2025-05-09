test:
	PYTHONPATH=. pytest \
		--cov=. \
		--cov-config=.coveragerc \
		--cov-report=term \
		--cov-report=html
