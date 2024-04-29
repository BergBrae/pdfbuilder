@echo off
REM Run pyinstaller
pyinstaller --noconsole --onefile --icon pdficon.ico main.py

REM copy to network drive
copy "dist\PDFBuilder.exe" "F:\data\PyPDFBuilder\PDFBuilder.exe"

REM copy code to network drive
copy "." "F:\data\PyPDFBuilder\code" /Y