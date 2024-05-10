@echo off
REM Run pyinstaller
pyinstaller PDFBuilder.spec
REM copy to network drive
copy "dist\PDFBuilder.exe" "G:\data\PDFBuilder.exe" /Y
copy "dist\PDFBuilder.exe" "C:\Users\guest2\Desktop\PDFBuilder.exe" /Y

pyinstaller PDFBuilder(AI).spec
copy "dist\PDFBuilder(AI).exe" "G:\data\PDFBuilder(AI).exe" /Y
copy "dist\PDFBuilder(AI).exe" "C:\Users\guest2\Desktop\PDFBuilder(AI).exe" /Y