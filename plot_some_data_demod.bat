@echo off
CALL activate py27
CALL cd d:\software_git_repos\Polaris\polaris_software
python plot_some_data.py demod
@echo on