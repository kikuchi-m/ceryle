@echo off
setlocal enabledelayedexpansion

del /Q %~dp0testargs

for %%a in (%*) do (
  echo %%a >> %~dp0testargs
)

npx chokidar^
 ceryle/*.py^
 ceryle/**/*.py^
 tests/*.py^
 tests/**/*.py^
 -c "%~dp0run_tests"^
 --initial
