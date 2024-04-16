@echo off
REM Run pyinstaller
echo %PATH%
pyinstaller --noconsole --onefile --icon pdficon.ico PDFBuilder.py