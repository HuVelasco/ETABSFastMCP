# 🛠️ Developer Guide - ETABS FastMCP

**Comprehensive guide for extending and customizing the ETABS FastMCP server**

## 🏗️ Architecture Deep Dive

### System Components

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ETABS FastMCP Architecture                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐                                                           │
│  │   Claude AI     │  Natural Language Commands                                │
│  │   Desktop       │  "Create a 5-story building..."                          │
│  └─────────┬───────┘                                                           │
│            │ MCP Protocol (JSON-RPC over stdio)                               │
│  ┌─────────▼───────┐                                                           │
│  │ Python FastMCP  │  @mcp.tool() decorated functions                         │
│  │ Server          │  - Input validation with Pydantic                        │
│  │                 │  - Error handling & logging                              │
│  │                 │  - Command routing                                        │
│  └─────────┬───────┘                                                           │
│            │ JSON Commands over stdio                                          │
│  ┌─────────▼───────┐                                                           │
│  │ C# ETABS        │  Command Processing:                                      │
│  │ Connector       │  - ETABSConnectionManager                                 │
│  │                 │  - PointManager (CRUD)                                    │
│  │                 │  - FrameManager (CRUD)                                    │
│  │                 │  - CommandProcessor (routing)                             │
│  └─────────┬───────┘                                                           │
│            │ COM API Calls                                                     │
│  ┌─────────▼───────┐                                                           │
│  │ ETABS Software  │  ETABSv1.dll COM Interface                               │
│  │                 │  - SapModel object                                        │
│  │                 │  - PointObj, FrameObj, etc.                              │
│  └─────────────────┘                                                           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Adding New ETABS API Functions

### Step-by-Step Process

#### 1. Identify ETABS API Requirements

First, consult the ETABS API documentation to understand:
- Required COM object methods
- Parameter types and formats
- Return value structures
- Error codes and handling

**Example**: Adding material property management

```csharp
// ETABS API research:
// sapModel.PropMaterial.SetMaterial(name, materialType, region, standardName, grade)
// sapModel.PropMaterial.GetMaterial(name, ref materialType, ref color, ref notes)
```

#### 2. Extend C# Models

Add new data structures in `Models/CommandModels.cs`:

```csharp
/// <summary>
/// Material property request
/// </summary>
public class MaterialRequest
{
    [JsonProperty("name")]
    public string Name { get; set; } = "";

    [JsonProperty("materialType")]
    public int MaterialType { get; set; } // 1=Steel, 2=Concrete, 3=Other

    [JsonProperty("region")]
    public string Region { get; set; } = "";

    [JsonProperty("standardName")]
    public string StandardName { get; set; } = "";

    [JsonProperty("grade")]
    public string Grade { get; set; } = "";

    [JsonProperty("properties")]
    public Dictionary<string, object>? Properties { get; set; }
}
```

#### 3. Create Manager Class

Create `Core/MaterialManager.cs`:

```csharp
using System;
using System.Collections.Generic;
using ETABSConnector.Models;

namespace ETABSConnector.Core
{
    /// <summary>
    /// Manages all material-related operations in ETABS
    /// </summary>
    public class MaterialManager
    {
        private readonly ETABSConnectionManager _connectionManager;

        public MaterialManager(ETABSConnectionManager connectionManager)
        {
            _connectionManager = connectionManager;
        }

        /// <summary>
        /// Create a new material in the ETABS model
        /// </summary>
        public CommandResponse CreateMaterial(MaterialRequest request)
        {
            if (!_connectionManager.IsConnected)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = "Not connected to ETABS"
                };
            }

            try
            {
                var sapModel = _connectionManager.SapModel!;

                // Create the material
                int ret = sapModel.PropMaterial.SetMaterial(
                    request.Name,
                    request.MaterialType,
                    request.Region,
                    request.StandardName,
                    request.Grade
                );

                if (ret != 0)
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = "Failed to create material in ETABS"
                    };
                }

                return new CommandResponse
                {
                    Success = true,
                    Data = new
                    {
                        name = request.Name,
                        type = request.MaterialType,
                        region = request.Region,
                        standard = request.StandardName,
                        grade = request.Grade,
                        message = "Material created successfully"
                    }
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error creating material: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Get material properties
        /// </summary>
        public CommandResponse GetMaterial(string materialName)
        {
            // Implementation similar to above...
        }

        // Add other CRUD operations...
    }
}
```

#### 4. Update Command Processor

In `Core/CommandProcessor.cs`, add the new manager and commands:

```csharp
public class CommandProcessor : IDisposable
{
    private readonly ETABSConnectionManager _connectionManager;
    private readonly PointManager _pointManager;
    private readonly FrameManager _frameManager;
    private readonly MaterialManager _materialManager; // Add this

    public CommandProcessor(TextReader? input = null, TextWriter? output = null, TextWriter? error = null)
    {
        // ... existing code ...
        _materialManager = new MaterialManager(_connectionManager); // Add this
    }

    private CommandResponse ProcessCommand(Command command)
    {
        try
        {
            return command.Action.ToLower() switch
            {
                // ... existing commands ...

                // Material commands
                "create_material" => ProcessMaterialCommand("create", command.Parameters),
                "get_material" => ProcessMaterialCommand("get", command.Parameters),
                "list_materials" => _materialManager.ListMaterials(),
                "modify_material" => ProcessMaterialCommand("modify", command.Parameters),
                "delete_material" => ProcessMaterialCommand("delete", command.Parameters),

                _ => new CommandResponse
                {
                    Success = false,
                    Error = $"Unknown command: {command.Action}"
                }
            };
        }
        catch (Exception ex)
        {
            return new CommandResponse
            {
                Success = false,
                Error = $"Error processing command '{command.Action}': {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Process material-specific commands
    /// </summary>
    private CommandResponse ProcessMaterialCommand(string operation, Dictionary<string, object> parameters)
    {
        try
        {
            return operation switch
            {
                "create" => _materialManager.CreateMaterial(ParseMaterialRequest(parameters)),
                "get" => _materialManager.GetMaterial(parameters.GetValueOrDefault("name", "") as string ?? ""),
                "modify" => _materialManager.ModifyMaterial(
                    parameters.GetValueOrDefault("name", "") as string ?? "",
                    ParseMaterialRequest(parameters)),
                "delete" => _materialManager.DeleteMaterial(parameters.GetValueOrDefault("name", "") as string ?? ""),
                _ => new CommandResponse { Success = false, Error = $"Unknown material operation: {operation}" }
            };
        }
        catch (Exception ex)
        {
            return new CommandResponse
            {
                Success = false,
                Error = $"Error in material operation '{operation}': {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Parse parameters into MaterialRequest object
    /// </summary>
    private MaterialRequest ParseMaterialRequest(Dictionary<string, object> parameters)
    {
        var request = new MaterialRequest();

        if (parameters.TryGetValue("name", out var nameObj))
            request.Name = nameObj as string ?? "";

        if (parameters.TryGetValue("materialType", out var typeObj))
            request.MaterialType = Convert.ToInt32(typeObj);

        if (parameters.TryGetValue("region", out var regionObj))
            request.Region = regionObj as string ?? "";

        if (parameters.TryGetValue("standardName", out var standardObj))
            request.StandardName = standardObj as string ?? "";

        if (parameters.TryGetValue("grade", out var gradeObj))
            request.Grade = gradeObj as string ?? "";

        return request;
    }
}
```

#### 5. Add Python FastMCP Tools

In `python-server/etabs_server.py`, add the corresponding MCP tools:

```python
@mcp.tool()
async def create_material(
    name: str,
    material_type: int,
    region: str = "US",
    standard_name: str = "AISC 360-16",
    grade: str = "A992Gr50"
) -> Dict[str, Any]:
    """
    Create a new material in the ETABS model
    
    Args:
        name: Material name (e.g., "Steel_A992")
        material_type: Material type (1=Steel, 2=Concrete, 3=Other)
        region: Material region/country (default: "US")
        standard_name: Standard specification (default: "AISC 360-16")
        grade: Material grade (default: "A992Gr50")
        
    Returns:
        Created material information
    """
    try:
        parameters = {
            "name": name,
            "materialType": material_type,
            "region": region,
            "standardName": standard_name,
            "grade": grade
        }
            
        response = await connector.send_command("create_material", parameters)
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_material(name: str) -> Dict[str, Any]:
    """
    Get information about a specific material
    
    Args:
        name: Material name
        
    Returns:
        Material properties and information
    """
    try:
        response = await connector.send_command("get_material", {"name": name})
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def list_materials() -> Dict[str, Any]:
    """
    List all materials in the ETABS model
    
    Returns:
        List of all materials with their properties
    """
    try:
        response = await connector.send_command("list_materials")
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## 🎯 Best Practices

### Error Handling

**Always wrap ETABS API calls:**
```csharp
try
{
    int ret = sapModel.SomeMethod(parameters);
    if (ret != 0)
    {
        return new CommandResponse
        {
            Success = false,
            Error = $"ETABS API returned error code: {ret}"
        };
    }
    // Success path...
}
catch (System.Runtime.InteropServices.COMException comEx)
{
    return new CommandResponse
    {
        Success = false,
        Error = $"COM Error: {comEx.Message} (HRESULT: {comEx.HResult:X8})"
    };
}
catch (Exception ex)
{
    return new CommandResponse
    {
        Success = false,
        Error = $"Unexpected error: {ex.Message}"
    };
}
```

### Parameter Validation

**Use Pydantic models in Python:**
```python
class MaterialRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Material name")
    material_type: int = Field(ge=1, le=3, description="Material type (1-3)")
    region: str = Field(default="US", description="Material region")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Material name must be alphanumeric with _ or - only')
        return v
```

### Logging and Debugging

**Add comprehensive logging:**
```csharp
private static readonly Logger logger = LogManager.GetCurrentClassLogger();

public CommandResponse CreateMaterial(MaterialRequest request)
{
    logger.Info($"Creating material: {request.Name} (Type: {request.MaterialType})");
    
    try
    {
        // ... implementation ...
        logger.Info($"Successfully created material: {request.Name}");
    }
    catch (Exception ex)
    {
        logger.Error(ex, $"Failed to create material: {request.Name}");
        throw;
    }
}
```

## 🔍 Testing New Features

### Unit Testing Framework

Create `Tests/MaterialManagerTests.cs`:

```csharp
using Microsoft.VisualStudio.TestTools.UnitTesting;
using ETABSConnector.Core;
using ETABSConnector.Models;

[TestClass]
public class MaterialManagerTests
{
    private MaterialManager _materialManager;
    private ETABSConnectionManager _connectionManager;

    [TestInitialize]
    public void Setup()
    {
        _connectionManager = new ETABSConnectionManager();
        _materialManager = new MaterialManager(_connectionManager);
    }

    [TestMethod]
    public void CreateMaterial_ValidRequest_ReturnsSuccess()
    {
        // Arrange
        var request = new MaterialRequest
        {
            Name = "Test_Steel",
            MaterialType = 1,
            Region = "US",
            StandardName = "AISC 360-16",
            Grade = "A992Gr50"
        };

        // Act & Assert would require ETABS connection
        // This is more of an integration test
    }
}
```

### Integration Testing

Create `Tests/IntegrationTests.py`:

```python
import asyncio
import unittest
from etabs_server import connector, create_material

class ETABSIntegrationTests(unittest.TestCase):
    
    async def test_material_creation_workflow(self):
        """Test complete material creation workflow"""
        
        # Connect to ETABS
        connect_result = await connector.send_command("connect")
        self.assertTrue(connect_result["success"])
        
        # Create blank model
        model_result = await connector.send_command("create_blank_model")
        self.assertTrue(model_result["success"])
        
        # Create material
        material_result = await create_material(
            name="Test_A992",
            material_type=1,
            region="US",
            standard_name="AISC 360-16",
            grade="A992Gr50"
        )
        self.assertTrue(material_result["success"])
        
        # Verify material exists
        get_result = await connector.send_command("get_material", {"name": "Test_A992"})
        self.assertTrue(get_result["success"])
        
        # Cleanup
        await connector.send_command("disconnect")

if __name__ == "__main__":
    unittest.main()
```

## 📈 Performance Optimization

### COM Object Management

**Minimize COM calls:**
```csharp
// Bad: Multiple API calls
var point1 = sapModel.PointObj.GetCoordCartesian(name1, ref x1, ref y1, ref z1);
var point2 = sapModel.PointObj.GetCoordCartesian(name2, ref x2, ref y2, ref z2);
var point3 = sapModel.PointObj.GetCoordCartesian(name3, ref x3, ref y3, ref z3);

// Better: Batch operations when possible
int numPoints = 0;
string[] pointNames = null;
double[] xCoords = null, yCoords = null, zCoords = null;
int ret = sapModel.PointObj.GetAllCoordCartesian(ref numPoints, ref pointNames, ref xCoords, ref yCoords, ref zCoords);
```

### Memory Management

**Proper disposal patterns:**
```csharp
public class ETABSConnectionManager : IDisposable
{
    private bool _disposed = false;

    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing)
            {
                // Dispose managed resources
                _sapModel = null;
            }
            
            // Release COM objects
            if (_sapObject != null)
            {
                System.Runtime.InteropServices.Marshal.ReleaseComObject(_sapObject);
                _sapObject = null;
            }
            
            _disposed = true;
        }
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }
}
```

## 🚀 Advanced Extensions

### Custom Analysis Functions

```csharp
public class AnalysisManager
{
    public CommandResponse RunAnalysis(string analysisType = "static")
    {
        var sapModel = _connectionManager.SapModel!;
        
        // Set analysis options
        sapModel.Analyze.SetRunCaseFlag("", true, true);
        
        // Run analysis
        int ret = sapModel.Analyze.RunAnalysis();
        
        if (ret == 0)
        {
            return new CommandResponse
            {
                Success = true,
                Data = new { message = "Analysis completed successfully" }
            };
        }
        else
        {
            return new CommandResponse
            {
                Success = false,
                Error = $"Analysis failed with code: {ret}"
            };
        }
    }
}
```

### Loading System

```csharp
public class LoadManager
{
    public CommandResponse CreateLoadPattern(string name, int loadType)
    {
        // eLoadPatternType: Dead=1, Live=2, Wind=3, etc.
        int ret = sapModel.LoadPatterns.Add(name, loadType);
        // Implementation...
    }
    
    public CommandResponse ApplyPointLoad(string pointName, string loadPattern, 
        double fx, double fy, double fz)
    {
        double[] forces = {fx, fy, fz, 0, 0, 0}; // Fx, Fy, Fz, Mx, My, Mz
        int ret = sapModel.PointObj.SetLoadForce(pointName, loadPattern, forces);
        // Implementation...
    }
}
```

## 📚 Resources

### ETABS API Documentation

- **CSI Knowledge Base**: https://wiki.csiamerica.com/
- **API Reference Manual**: Included with ETABS installation
- **COM Interface Guide**: `CSi API ETABS v1.chm`

### Useful ETABS Objects

```csharp
// Most commonly used ETABS API objects:
sapModel.PointObj       // Point objects
sapModel.FrameObj       // Frame elements  
sapModel.AreaObj        // Area elements
sapModel.SolidObj       // Solid elements
sapModel.LinkObj        // Link elements
sapModel.PropMaterial   // Material properties
sapModel.PropFrame      // Frame sections
sapModel.PropArea       // Area sections
sapModel.LoadPatterns   // Load patterns
sapModel.LoadCases      // Load cases
sapModel.Analyze        // Analysis functions
sapModel.Results        // Analysis results
sapModel.File           // File operations
sapModel.View           // View control
```

### Error Code Reference

```csharp
// Common ETABS API return codes:
// 0 = Success
// 1 = General failure
// 2 = Object not found
// 3 = Invalid input
// 4 = Analysis not run
// 5 = Analysis failed
```

---

**Happy coding! 🚀**

*This developer guide provides the foundation for extending the ETABS FastMCP server with any ETABS API functionality. Follow these patterns for consistent, maintainable, and professional-grade code.*