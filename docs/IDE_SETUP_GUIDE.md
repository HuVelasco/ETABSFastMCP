# 🛠️ IDE Setup Guide - ETABS FastMCP

**Complete guide for setting up your development environment**

## 🎯 Recommended IDE: **Visual Studio** (Best Choice)

### Why Visual Studio?

**Visual Studio is the best choice for this project because:**

✅ **Native C# Support**: Excellent IntelliSense, debugging, and COM interop support
✅ **ETABS Integration**: Perfect handling of COM references and ETABSv1.dll
✅ **Project Templates**: Built-in .NET Framework project support
✅ **NuGet Integration**: Easy package management for Newtonsoft.Json
✅ **Debugging**: Superior debugging for C# COM objects
✅ **MSBuild Integration**: Seamless building without command line issues

### Visual Studio Setup

#### 1. Download and Install

**Visual Studio 2022 Community (Free)**: https://visualstudio.microsoft.com/vs/community/

**Required Workloads:**
- ✅ .NET desktop development
- ✅ Desktop development with C++  (for COM support)

**Individual Components to Add:**
- ✅ .NET Framework 4.8 targeting pack
- ✅ .NET Framework 4.8 SDK
- ✅ MSBuild
- ✅ NuGet package manager

#### 2. Open the Project

1. **Launch Visual Studio 2022**
2. **File → Open → Project/Solution**
3. **Navigate to**: `ETABSFastMCP/csharp-connector/ETABSConnector.csproj`
4. **Click Open**

#### 3. Configure ETABS Reference

**If you get "ETABSv1 reference not found" error:**

1. **Right-click References** in Solution Explorer
2. **Add Reference → Browse**
3. **Navigate to ETABS installation**:
   ```
   C:\Program Files\Computers and Structures\ETABS 18\ETABSv1.dll
   ```
4. **Select ETABSv1.dll → OK**

#### 4. Build and Test

1. **Build → Build Solution** (Ctrl+Shift+B)
2. **Debug → Start Debugging** (F5) or **Start Without Debugging** (Ctrl+F5)

### Project Structure in Visual Studio

```
ETABSConnector
├── 📁 References
│   ├── ETABSv1 (COM Reference)
│   ├── Newtonsoft.Json (NuGet Package)
│   └── System References
├── 📁 Core
│   ├── ETABSConnectionManager.cs
│   ├── PointManager.cs
│   ├── FrameManager.cs
│   └── CommandProcessor.cs
├── 📁 Models
│   └── CommandModels.cs
├── 📁 Properties
│   └── AssemblyInfo.cs
├── Program.cs
├── App.config
└── ETABSConnector.csproj
```

---

## 🔄 Alternative: **VS Code** (Secondary Choice)

### Why VS Code as Secondary?

✅ **Lightweight**: Fast startup and good performance
✅ **Python Support**: Excellent for the Python FastMCP server
✅ **Multi-language**: Handle both C# and Python in one environment
⚠️ **Limited C# Features**: Less robust IntelliSense for C# COM objects
⚠️ **Manual Setup**: Requires more configuration for .NET Framework

### VS Code Setup

#### 1. Install VS Code and Extensions

**Download**: https://code.visualstudio.com/

**Required Extensions:**
```
# C# Support
ms-dotnettools.csharp
ms-dotnettools.vscode-dotnet-runtime

# Python Support  
ms-python.python
ms-python.pylint

# Helpful Extensions
ms-vscode.vscode-json
ms-vscode.powershell
```

#### 2. Install .NET Framework Developer Pack

**Download**: https://dotnet.microsoft.com/download/dotnet-framework/net48

**Required Components:**
- .NET Framework 4.8 Developer Pack
- .NET Framework 4.8 Targeting Pack

#### 3. Configure Workspace

**Create `.vscode/settings.json`:**
```json
{
    "python.defaultInterpreterPath": "python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "files.associations": {
        "*.csproj": "xml"
    },
    "msbuild.dotnetPath": "C:\\Program Files\\dotnet\\dotnet.exe"
}
```

**Create `.vscode/tasks.json`:**
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "build-csharp",
            "type": "shell",
            "command": "msbuild",
            "args": [
                "csharp-connector/ETABSConnector.csproj",
                "/p:Configuration=Debug"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "run-python-server",
            "type": "shell",
            "command": "python",
            "args": ["python-server/etabs_server.py"],
            "group": "test"
        },
        {
            "label": "run-demo",
            "type": "shell", 
            "command": "python",
            "args": ["examples/simple_demo.py"],
            "group": "test"
        }
    ]
}
```

#### 4. Building in VS Code

**Option 1 - Command Palette:**
1. **Ctrl+Shift+P** → **Tasks: Run Task**
2. **Select "build-csharp"**

**Option 2 - Terminal:**
```bash
# Navigate to csharp-connector directory
cd csharp-connector

# Build using MSBuild (if available)
msbuild ETABSConnector.csproj /p:Configuration=Debug

# Or use dotnet (if converted to .NET Core)
dotnet build
```

---

## 🐍 Python Environment Setup

### 1. Python Installation

**Python 3.8+ Required**: https://www.python.org/downloads/

**Verify Installation:**
```bash
python --version
pip --version
```

### 2. Install Dependencies

```bash
# Navigate to python-server directory
cd python-server

# Install requirements
pip install -r requirements.txt

# Or install individually:
pip install mcp>=1.0.0 asyncio pydantic>=2.0.0 typing-extensions>=4.0.0
```

### 3. Test Python Server

```bash
# Test the server directly
python etabs_server.py

# Run the demo
cd ../examples
python simple_demo.py
```

---

## 🔨 Build Scripts

### Windows Batch Script

**Use the provided `build.bat`:**
```batch
# From the ETABSFastMCP directory:
build.bat
```

**What it does:**
1. Locates MSBuild automatically
2. Builds the C# connector
3. Reports success/failure
4. Provides next steps

### Manual Build Commands

**If build.bat doesn't work:**

```batch
# Find your Visual Studio installation
dir "C:\Program Files*\Microsoft Visual Studio"

# Use the appropriate MSBuild path:
"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" ^
  csharp-connector\ETABSConnector.csproj ^
  /p:Configuration=Debug /p:Platform=AnyCPU
```

---

## 🚀 Getting Started Workflow

### Recommended Development Flow

1. **Open in Visual Studio**:
   - Load `ETABSConnector.csproj`
   - Build and test C# connector

2. **Use VS Code for Python**:
   - Open the entire `ETABSFastMCP` folder
   - Develop and test Python server

3. **Terminal for Testing**:
   - Run demos and integration tests
   - Test Claude Desktop configuration

### Development Setup

```bash
# 1. Clone/navigate to project
cd ETABSFastMCP

# 2. Build C# connector (Visual Studio or build.bat)
build.bat

# 3. Install Python dependencies
cd python-server
pip install -r requirements.txt

# 4. Test the system
cd ../examples
python simple_demo.py

# 5. Configure Claude Desktop
# Copy config/claude_desktop_config.json to Claude Desktop settings
```

---

## 🔍 Troubleshooting

### Common Issues

#### C# Build Issues

**"MSBuild not found"**
```bash
# Install Visual Studio 2022 with .NET desktop development workload
# Or install Build Tools for Visual Studio 2022
```

**"ETABSv1.dll not found"**
```bash
# Update the reference path in ETABSConnector.csproj:
<Reference Include="ETABSv1">
  <HintPath>C:\Program Files\Computers and Structures\ETABS 18\ETABSv1.dll</HintPath>
</Reference>
```

**"Newtonsoft.Json not found"**
```bash
# Restore NuGet packages in Visual Studio:
# Tools → NuGet Package Manager → Package Manager Console
# Run: Update-Package -reinstall
```

#### Python Issues

**"mcp module not found"**
```bash
# Install MCP package:
pip install mcp>=1.0.0

# Or use virtual environment:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt  
```

#### Integration Issues

**"Connector process not starting"**
1. Verify C# connector builds successfully
2. Check executable path in Python server
3. Ensure .NET Framework 4.8 is installed
4. Run connector manually to test

---

## 📚 Recommended Extensions

### Visual Studio Extensions

- **Python Development** (if working with both languages)
- **JSON Editor** (for configuration files)
- **Markdown Editor** (for documentation)

### VS Code Extensions

```
# Essential
ms-dotnettools.csharp
ms-python.python

# Helpful
ms-vscode.vscode-json
redhat.vscode-yaml
ms-vscode.powershell
ms-python.pylint
ms-python.black-formatter
```

---

## 🎯 Final Recommendations

### Best Setup for This Project:

1. **Visual Studio 2022** for C# development
2. **VS Code** for Python and mixed development
3. **Windows Terminal** for testing and demos
4. **Claude Desktop** for end-user testing

### Why This Combination Works:

- **Visual Studio** handles C# COM objects perfectly
- **VS Code** provides excellent Python support
- **Both IDEs** can work with the same codebase
- **Easy switching** between languages and tools

---

**You're now ready to develop and extend the ETABS FastMCP server! 🚀**