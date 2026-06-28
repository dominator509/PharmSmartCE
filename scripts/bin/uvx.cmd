@echo off
py -3.14 -m uv tool run %*
exit /b %errorlevel%
