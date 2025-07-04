@echo off
REM ==== aktywuj venv i uruchom main.py ====

REM • ustal katalog w którym leży ten plik
set "ROOT=%~dp0"

REM • aktywuj virtual-env
call "%ROOT%venv\Scripts\activate.bat"

REM • przejdź do folderu z kodem i odpal skrypt
pushd "%ROOT%tricoma-shopware-copier"
python main.py
popd

pause
