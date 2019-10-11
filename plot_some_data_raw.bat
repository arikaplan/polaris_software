@echo off
CALL activate py27
echo Done.
CALL cd d:\software_git_repos\Polaris\polaris_software
CALL python plot_some_data.py raw
@echo on