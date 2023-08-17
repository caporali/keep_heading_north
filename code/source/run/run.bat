@REM run on the venv khn_env_3.11 built on python 3.11.4
@echo off
powershell -ExecutionPolicy RemoteSigned -File .\run.ps1
cmd /k
exit /B 0