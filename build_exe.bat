@echo off
REM Run pyinstaller
pyinstaller --noconsole --onefile --icon pdficon.ico PDFBuilder.py

REM copy to network drive
copy "dist\PDFBuilder.exe" "G:\data\PyPDFBuilder\PDFBuilder.exe"

REM copy code to network drive
copy "." "G:\data\PyPDFBuilder\code" /Y

copy "llamafiles\*.exe" "G:\data\PyPDFBuilder\llamafiles" /Y