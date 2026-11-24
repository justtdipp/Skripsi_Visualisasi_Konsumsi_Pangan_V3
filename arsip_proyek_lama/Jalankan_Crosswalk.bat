@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo ==========================================================
echo PEMETAAN OTOMATIS WILAYAH BAPANAS - BPS 2021-2023
echo ==========================================================

%PYTHON_EXE% -m pip install pandas requests
if errorlevel 1 (
    echo Gagal memasang kebutuhan Python.
    pause
    exit /b 1
)

%PYTHON_EXE% buat_crosswalk_bps.py
if errorlevel 1 (
    echo Proses belum berhasil. Baca pesan error di atas.
    pause
    exit /b 1
)

echo.
echo Proses selesai. Hasil tersimpan di data\hasil_validasi\
pause
