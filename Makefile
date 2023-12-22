PYTHON = python
SCRIPT = gatorLibrary.py

# Testcase can be overridden as TEST_CASE='testcase8.txt'
TEST_CASE = 'testcase1.txt'

run:
	$(PYTHON) $(SCRIPT) $(TEST_CASE)

.PHONY: run