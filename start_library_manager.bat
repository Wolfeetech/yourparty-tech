@echo off
title YourParty Library Manager
echo Starting Library Manager Service...
echo Monitoring Z:\yourparty_Libary\Inbox
:loop
python c:\Users\StudioPC\yourparty-tech\apps\api\manager_service.py
echo Crashing... Restarting in 5 seconds...
timeout /t 5
goto loop
