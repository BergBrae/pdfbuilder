@echo off
REM Run pyinstaller
pyinstaller PDFBuilder.spec

REM copy to network drive
copy "dist\PDFBuilder.exe" "G:\data\PDFBuilder.exe" /Y
copy "dist\PDFBuilder.exe" "C:\Users\guest2\Desktop\PDFBuilder.exe" /Y