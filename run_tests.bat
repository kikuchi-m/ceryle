:: @echo off
setlocal enabledelayedexpansion

set TESTARGS=
for /F %%a in (%~dp0testargs) do (
  set TESTARGS=!TESTARGS! %%a
)

python -m flake8 --exit-zero ceryle/ tests/
python -m pytest !TESTARGS!
