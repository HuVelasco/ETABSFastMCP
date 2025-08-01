@echo off
echo Building ETABS FastMCP Connector...
echo.

REM Try to find MSBuild
set MSBUILD_PATH=""
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe" (
    set MSBUILD_PATH="C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe" (
    set MSBUILD_PATH="C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe" (
    set MSBUILD_PATH="C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe"
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" (
    set MSBUILD_PATH="C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
)

if %MSBUILD_PATH%=="" (
    echo ERROR: MSBuild not found. Please install Visual Studio 2019+ or Build Tools.
    echo.
    echo You can also try building in Visual Studio by opening:
    echo   ETABSConnector.csproj
    echo.
    pause
    exit /b 1
)

echo Using MSBuild at: %MSBUILD_PATH%
echo.

REM Build the project
cd csharp-connector
%MSBUILD_PATH% ETABSConnector.csproj /p:Configuration=Debug /p:Platform=AnyCPU

if %ERRORLEVEL% == 0 (
    echo.
    echo ✅ Build successful!
    echo Executable location: csharp-connector\bin\Debug\ETABSConnector.exe
    echo.
    echo You can now run the Python test script:
    echo   python examples\test_batch_operations.py
) else (
    echo.
    echo ❌ Build failed with error code %ERRORLEVEL%
    echo.
    echo Common issues:
    echo - ETABS not installed (ETABSv1.dll not found)
    echo - .NET Framework 4.8 not installed  
    echo - Newtonsoft.Json package not restored
)

echo.
pause