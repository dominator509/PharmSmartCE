@echo off
py -3.14 -m uv %*
exit /b %errorlevel%
