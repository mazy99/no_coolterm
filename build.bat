@echo off
echo Building ModbusTerminal...
cd src
python -m PyInstaller --onefile --windowed --name="ModbusTerminal" main.py
copy /Y dist\ModbusTerminal.exe ..\
cd ..
echo Done!
pause