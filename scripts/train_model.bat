@echo off
cd /d %~dp0\..
python training\train_model.py
python training\model_audit.py
pause
