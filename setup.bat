@echo off

echo "Python version should be 3.10 or higher"
mkdir -p ./venv
python -m venv ./venv

call .\venv\bin\activate.bat
pip install -r ./requirements.txt
