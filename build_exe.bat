@echo off
REM Run pyinstaller
echo %PATH%
pyinstaller --noconsole --onefile --icon pdficon.ico PDFBuilder.py

REM copy to network drive
copy "dist\PDFBuilder.exe" "F:\data\PyPDFBuilder\PDFBuilder.exe"