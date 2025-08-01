# 🏗️ ETABS FastMCP Server

**Professional-grade MCP server for ETABS structural analysis integration with Claude Desktop**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![.NET Framework 4.8](https://img.shields.io/badge/.NET-4.8-purple.svg)](https://dotnet.microsoft.com/download/dotnet-framework/net48)

## 🌟 Overview

The ETABS FastMCP Server provides seamless integration between Claude Desktop and ETABS (Extended Three-Dimensional Analysis of Building Systems) structural analysis software. This professional-grade solution uses a hybrid Python+C# architecture optimized for scalability, reliability, and ease of use.

### 🏛️ Architecture

```
┌─────────────────┐    JSON/stdio    ┌───────────────────┐    COM API    ┌─────────────┐
│   Claude AI     │ ◄────────────► │ Python FastMCP    │ ◄──────────► │ C# Connector │ ◄──────► │   ETABS    │
│   Desktop       │                 │ Server            │               │              │          │ Software   │
└─────────────────┘                 └───────────────────┘               └─────────────┘          └─────────────┘
```

**Key Components:**
- **Python FastMCP Server**: High-level MCP interface with @mcp.tool() decorators
- **C# ETABS Connector**: Robust COM interface manager for ETABS API
- **JSON Communication**: Efficient stdio-based messaging between components

## 🚀 Quick Start

### Prerequisites

1. **ETABS Software**: ETABS v18+ installed and licensed
2. **Python 3.8+**: With pip package manager
3. **Visual Studio 2019+**: Or MSBuild tools for C# compilation
4. **Claude Desktop**: Latest version

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ETABSFastMCP
   ```

2. **Install Python dependencies:**
   ```bash
   cd python-server
   pip install -r requirements.txt
   ```

3. **Build the C# connector:**
   ```bash
   cd ../csharp-connector
   msbuild ETABSConnector.csproj /p:Configuration=Release
   ```

4. **Configure Claude Desktop:**
   - Copy `config/claude_desktop_config.json` content to your Claude Desktop config
   - Update paths to match your installation directory

### First Run

1. **Start ETABS** (optional - server can auto-start)

2. **Test the connection:**
   ```python
   # In Claude Desktop, try:
   "Connect to ETABS and create a new blank model"
   ```

3. **Create your first structural elements:**
   ```python
   # Example commands for Claude:
   "Create a point at coordinates (0, 0, 0) with UZ restraint"
   "Create a frame from (0, 0, 0) to (10, 0, 0) with W14X90 section"
   ```

## 🔧 Available Tools

### Connection Management
- `connect_to_etabs()` - Connect to ETABS application
- `create_blank_model()` - Create new blank model
- `get_connection_status()` - Check connection status
- `disconnect_from_etabs()` - Disconnect from ETABS

### Point Operations (CRUD)
- `create_point(x, y, z, name?, restraints?)` - Create structural point
- `get_point(name)` - Get point information
- `list_points()` - List all points in model
- `modify_point(name, x?, y?, z?, restraints?)` - Modify point properties
- `delete_point(name)` - Delete point from model

### Frame Operations (CRUD)  
- `create_frame(start_x, start_y, start_z, end_x, end_y, end_z, name?, section?, material?)` - Create frame element
- `get_frame(name)` - Get frame information
- `list_frames()` - List all frames in model
- `modify_frame(name, section?, material?)` - Modify frame properties
- `delete_frame(name)` - Delete frame from model

### Model Management
- `save_model(file_path?)` - Save current model
- `health_check()` - Check system health

## 💡 Usage Examples

### Basic Structural Model Creation

```python
# Through Claude Desktop conversation:

"Connect to ETABS and create a new blank model"

"Create the following points:
- Point A at (0, 0, 0) with UX, UY, UZ restraints
- Point B at (10, 0, 0) with UZ restraint  
- Point C at (10, 10, 0) with UZ restraint
- Point D at (0, 10, 0) with UZ restraint"

"Create frames connecting these points to form a rectangular frame:
- Frame AB from point A to B using W14X90 section
- Frame BC from point B to C using W14X90 section  
- Frame CD from point C to D using W14X90 section
- Frame DA from point D to A using W14X90 section"

"List all frames in the model and show their properties"
```

### Advanced Operations

```python
"Create a 3D building frame:
1. Create a 4x4 grid of points at elevation 0, spacing 8m
2. Create another identical grid at elevation 4m  
3. Connect corresponding points with vertical columns using W14X74 sections
4. Connect points at each level with beams using W21X50 sections
5. Apply pinned restraints to all base points"
```

## 🔧 Extending the System

### Adding New ETABS API Functions

The system is designed for easy extension. To add new ETABS functionality:

1. **Add to C# Connector:**
   ```csharp
   // In CommandProcessor.cs, add new case:
   "your_new_command" => ProcessYourNewCommand(command.Parameters),
   
   // Implement the method:
   private CommandResponse ProcessYourNewCommand(Dictionary<string, object> parameters)
   {
       // Your ETABS API calls here
       return new CommandResponse { Success = true, Data = result };
   }
   ```

2. **Add to Python Server:**
   ```python
   @mcp.tool()
   async def your_new_function(param1: str, param2: float) -> Dict[str, Any]:
       """
       Description of your new function
       """
       try:
           response = await connector.send_command("your_new_command", {
               "param1": param1,
               "param2": param2
           })
           return response
       except Exception as e:
           return {"success": False, "error": str(e)}
   ```

### Common Extensions

**Analysis Operations:**
- Run analysis
- Get analysis results
- Extract forces and moments

**Loading Operations:**
- Create load patterns
- Apply loads to elements
- Load combinations

**Design Operations:**
- Run steel design
- Get design results
- Optimize sections

## 🏗️ Professional Features

### Error Handling & Recovery
- Comprehensive exception handling throughout
- Automatic process recovery on crashes
- Detailed error logging and reporting

### Performance Optimization
- Efficient JSON serialization
- Minimal memory footprint
- Optimized COM object management

### Scalability
- Modular architecture for easy extension
- Clean separation of concerns
- Professional code organization

### Production Readiness
- Comprehensive logging
- Health monitoring
- Graceful shutdown handling
- Resource cleanup

## 🔍 Troubleshooting

### Common Issues

**Connection Errors:**
```
Error: "Failed to start ETABS connector"
- Ensure ETABS is installed and licensed
- Check that ETABSv1.dll is accessible
- Verify .NET Framework 4.8 is installed
```

**Permission Issues:**
```
Error: "Access denied to ETABS API"
- Run as Administrator if needed
- Check ETABS licensing status
- Verify COM object registration
```

**Communication Errors:**
```
Error: "No response from ETABS connector"
- Check C# connector build successful
- Verify Python can execute connector
- Check process permissions
```

### Debug Mode

Enable detailed logging by setting environment variable:
```bash
set ETABS_MCP_DEBUG=1
```

## 📚 API Reference

### Data Types

**Point3D:**
```json
{
  "x": 0.0,
  "y": 0.0, 
  "z": 0.0
}
```

**Restraints:**
```json
{
  "UX": true,   // Translation X
  "UY": false,  // Translation Y  
  "UZ": true,   // Translation Z
  "RX": false,  // Rotation X
  "RY": false,  // Rotation Y
  "RZ": false   // Rotation Z
}
```

**Frame Properties:**
```json
{
  "name": "F1",
  "startPoint": {"x": 0, "y": 0, "z": 0},
  "endPoint": {"x": 10, "y": 0, "z": 0},
  "section": "W14X90",
  "material": "A992",
  "length": 10.0
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- CSI (Computers & Structures, Inc.) for ETABS software
- Anthropic for Claude and MCP protocol
- FastMCP library contributors

---

**Built with ❤️ for the structural engineering community**

*This is a professional-grade, production-ready solution designed for real-world structural engineering workflows.*