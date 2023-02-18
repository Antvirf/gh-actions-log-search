get-repos:
	python 1_get_repos_and_workflow_runs.py

get-logs:
	python 2_get_logs_for_workflow_runs.py

get-words:
	python 3_find_words_in_logs.py

full-run: get-repos get-logs get-words

clean:
	@rm -rf logs/*
	@rm -rf logs_extracted/*
	@rm -f matched_lines.json
	@rm -f repo_run_ids.json