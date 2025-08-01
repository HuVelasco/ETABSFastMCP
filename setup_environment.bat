@echo off
echo ===============================================
echo   ETABS FastMCP Environment Setup
echo   Authors: Hugo & BIM Master
echo ===============================================
echo.

REM Navigate to project directory
cd /d "%~dp0"

echo 1. Setting up Python Virtual Environment...
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to create virtual environment
        echo Make sure Python 3.8+ is installed and in PATH
        pause
        exit /b 1
    )
    echo SUCCESS: Virtual environment created
) else (
    echo Virtual environment already exists
)

echo.
echo 2. Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo SUCCESS: Virtual environment activated
echo.

echo 3. Installing Python dependencies...
pip install --upgrade pip
pip install -r python-server\requirements.txt

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Trying individual packages...
    pip install mcp>=1.0.0
    pip install asyncio
    pip install pydantic>=2.0.0
    pip install typing-extensions>=4.0.0
)

echo SUCCESS: Dependencies installed
echo.

echo 4. Building C# Connector...
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
    echo WARNING: MSBuild not found automatically
    echo Please build manually in Visual Studio:
    echo   1. Open: csharp-connector\ETABSConnector.csproj
    echo   2. Build -> Build Solution
    echo.
) else (
    echo Building with MSBuild...
    %MSBUILD_PATH% csharp-connector\ETABSConnector.csproj /p:Configuration=Debug /p:Platform=AnyCPU
    
    if %ERRORLEVEL% == 0 (
        echo SUCCESS: C# connector built successfully
    ) else (
        echo WARNING: Build failed - try building in Visual Studio
    )
)

echo.
echo 5. Testing the setup...
echo.

echo Running mock demo...
python examples\simple_demo.py

echo.
echo ===============================================
echo   SETUP COMPLETE!
echo ===============================================
echo.
echo Your project paths:
echo   C# Project: %CD%\csharp-connector\ETABSConnector.csproj
echo   Python Server: %CD%\python-server\etabs_server.py
echo   Examples: %CD%\examples\
echo.
echo Next steps:
echo   1. Open Visual Studio and load the .csproj file
echo   2. Test with: python examples\simple_demo.py
echo   3. Set up Claude Desktop (see config\claude_desktop_config.json)
echo   4. Install MCP Inspector: npm install -g @modelcontextprotocol/inspector
echo.
echo To reactivate virtual environment later:
echo   cd %CD%
echo   venv\Scripts\activate.bat
echo.
pause