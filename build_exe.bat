@echo off
REM Run pyinstaller
pyinstaller --noconsole --onefile --icon pdficon.ico -n PDFBuilder main.py

REM copy to network drive
copy "dist\PDFBuilder.exe" "G:\data\PyPDFBuilder\PDFBuilder.exe"

REM copy code to network drive
copy "." "G:\data\PyPDFBuilder\code" /Y

REM copy "llamafiles\*.exe" "G:\data\PyPDFBuilder\llamafiles" /Y