@echo off
REM Run pyinstaller
echo %PATH%
pyinstaller --noconsole --onefile --icon pdficon.ico PDFBuilder.py

REM Copy the project directory to a network drive
xcopy /E /I /Y "C:\Users\guest2\development\pdfbuilder" "F:/data/PyPDFBuilder"