# ETABS FastMCP System - Complete Documentation

## 🎯 Project Vision

Create an AI-powered structural engineering automation system that allows engineers to use natural language to control ETABS, Tekla, and other CAD software through Claude AI.

**Target Workflow:** *"Create a 40-foot rigid frame with 16-foot columns"* → Claude automatically creates the structure in ETABS and Tekla.

## 🏗️ System Architecture (Simple Terms)

Think of our system like a **Universal Translator for Engineering Software:**

```
👤 Engineer (speaks English) 
    ↕️ 
🤖 Claude AI (understands English, speaks MCP) 
    ↕️ 
🐍 Python Server (translates MCP to HTTP) 
    ↕️ 
🔷 C# Connector (translates HTTP to ETABS/Tekla API) 
    ↕️ 
🏗️ ETABS/Tekla (creates 3D models)
```

### Component Explanations

#### 1. **Claude AI** (The Smart Assistant)
- **What it does:** Understands your English commands like "create a beam"
- **How it works:** Uses MCP (Model Context Protocol) to call tools
- **Example:** You say "make a column" → Claude calls `create_column()` tool

#### 2. **Python MCP Server** (The Translator)
- **What it does:** Converts Claude's tool calls into HTTP requests
- **How it works:** Receives MCP messages, sends HTTP to C# server
- **Example:** `create_column()` → `POST /create-column` to C# server

#### 3. **C# Connector** (The CAD Controller)
- **What it does:** Actually controls ETABS and Tekla software
- **How it works:** Uses official software APIs (COM/NET)
- **Example:** HTTP request → `sapModel.FrameObj.AddByCoord()` in ETABS

#### 4. **UBIM (Universal Building Information Model)** (The Smart Memory)
- **What it does:** Remembers everything about your building across all software
- **How it works:** Central database that syncs data between ETABS, Tekla, etc.
- **Example:** You change a beam in ETABS → UBIM updates Tekla automatically

## 🎯 Current Target: Pre-Engineered Rigid Frame

### What We're Building First
A simple 2D building frame with:
- 2 columns (vertical supports)
- 2 sloped beams (roof structure)
- Rigid connections (moment-resisting)

```
    Beam 2 (sloped)
   /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\
  /                    \
 /  Beam 1 (sloped)     \
/                        \
|                        |
| Column 1    Column 2   |
|                        |
└────────────────────────┘
```

### Why This Frame?
- **Simple:** Only 4 members (2 columns + 2 beams)
- **Real:** Actual structural engineering workflow
- **Testable:** Easy to verify results
- **Scalable:** Foundation for complex structures

## 🛠️ Implementation Plan

### Phase 1: Basic Tool Creation (This Week)
**Goal:** Get one simple command working end-to-end

1. **Create UBIM Schema** - Define how we store frame data
2. **Create Python MCP Tool** - `create_rigid_frame()` function
3. **Create C# Handler** - Connects to ETABS and creates the frame
4. **Test with Claude** - "Create a 40ft by 16ft rigid frame"

### Phase 2: ETABS Integration (Next Week)
**Goal:** Full ETABS structural analysis workflow

1. **Add Analysis Tools** - Run structural analysis
2. **Add Results Tools** - Get forces, deflections, reactions
3. **Add Design Tools** - Check code compliance, optimize sizes

### Phase 3: Tekla Integration (Week 3)
**Goal:** Fabrication-ready models

1. **Sync ETABS → Tekla** - Transfer geometry and properties
2. **Add Connection Details** - Bolts, welds, plates
3. **Generate Drawings** - Fabrication and erection drawings

### Phase 4: UBIM Coordination (Week 4)
**Goal:** Seamless multi-software workflow

1. **Central Model Management** - All changes flow through UBIM
2. **Conflict Resolution** - Handle disagreements between software
3. **Version Control** - Track all changes with timestamps

## 🎮 User Experience Vision

### Current Workflow (Manual)
```
1. Open ETABS → Create points manually → Create frames manually
2. Define sections → Assign loads → Run analysis  
3. Check results → Export to Excel → Email to team
4. Open Tekla → Recreate same geometry → Add connections
5. Generate drawings → Check drawings → Revise drawings
Time: 4-8 hours for simple frame
```

### Future Workflow (AI-Powered)
```
Engineer: "Create a 40-foot rigid frame, analyze it, and prepare for fabrication"

Claude: 
✅ Created rigid frame (40' span, 16' eave height)
✅ Ran structural analysis - all members OK
✅ Synced to Tekla with standard connections
✅ Generated fabrication drawings
✅ Ready for review!

Time: 2 minutes
```

## 📋 Detailed Technical Specifications

### UBIM Data Schema
```python
class RigidFrameUBIM:
    # Geometry Parameters
    span: float              # Building width (ft)
    eave_height: float       # Column height (ft)
    peak_height: float       # Total height at peak (ft)
    roof_slope: float        # Slope (in/ft)
    
    # Structural Properties  
    column_section: str      # "W14X68"
    beam_section: str        # "W21X50" 
    steel_grade: str         # "A992"
    
    # Connection Details
    base_connection: str     # "fixed" or "pinned"
    beam_column_connection: str  # "rigid" or "pinned"
    
    # Calculated Geometry
    points: dict            # Coordinate locations
    members: dict           # Member definitions
    
    # Software Sync Status
    synced_to: dict         # Which software has current version
```

### MCP Tool Signatures
```python
@mcp.tool()
async def create_rigid_frame(
    span: float,                    # Building width in feet
    eave_height: float,             # Column height in feet
    roof_slope: float,              # Roof slope in inches per foot
    column_section: str = "W14X68", # Column profile
    beam_section: str = "W21X50",   # Beam profile
    steel_grade: str = "A992"       # Material grade
) -> dict:
    """Create a 2D rigid frame for pre-engineered building"""

@mcp.tool()
async def sync_frame_to_etabs(frame_id: str) -> dict:
    """Send rigid frame to ETABS for structural analysis"""

@mcp.tool()
async def sync_frame_to_tekla(frame_id: str) -> dict:
    """Send rigid frame to Tekla for fabrication detailing"""

@mcp.tool()
async def analyze_frame(frame_id: str) -> dict:
    """Run structural analysis and return results"""
```

### C# API Handlers
```csharp
// Universal API call handler
public CommandResponse CallAPI(APICallRequest request)
{
    switch (request.APIPath)
    {
        case "RigidFrame.Create":
            return CreateRigidFrame(request.Parameters);
        case "RigidFrame.SyncToETABS":
            return SyncToETABS(request.Parameters);
        case "RigidFrame.SyncToTekla":
            return SyncToTekla(request.Parameters);
    }
}
```

## 🚀 Getting Started Tutorial

### Step 1: Environment Setup
1. **Install ETABS** (version 18+)
2. **Install Visual Studio** (Community edition)
3. **Install Python 3.8+** with pip
4. **Install Claude Desktop** application

### Step 2: Create C# Project
1. New Console App (.NET Framework 4.8)
2. Add ETABS reference: `ETABSv1.dll`
3. Add HTTP server capability
4. Test ETABS connection

### Step 3: Create Python MCP Server
1. Install FastMCP: `pip install fastmcp`
2. Create basic MCP server structure
3. Define first tool: `create_rigid_frame`
4. Test MCP protocol communication

### Step 4: Configure Claude Desktop
1. Add MCP server to `claude_desktop_config.json`
2. Restart Claude Desktop
3. Verify tool connection (tool count should increase)
4. Test first command: "Create a simple rigid frame"

## 🎯 Success Metrics

### Week 1 Success Criteria
- [ ] Claude can create a rigid frame with natural language
- [ ] Frame appears correctly in ETABS
- [ ] All 4 members (2 columns, 2 beams) are created
- [ ] Member sections are assigned correctly
- [ ] Points are positioned accurately

### Month 1 Success Criteria  
- [ ] Full ETABS analysis workflow
- [ ] ETABS ↔ Tekla synchronization
- [ ] UBIM manages data consistency
- [ ] Drawing generation automation
- [ ] 70%+ time savings on rigid frame workflows

## 🔄 Continuation Prompt for New Chat

**If starting a new chat, use this prompt:**

---

**CONTINUATION PROMPT:**

I'm building an AI-powered structural engineering system called "ETABS FastMCP" that allows engineers to control ETABS and Tekla using natural language through Claude AI.

**System Architecture:**
- Claude AI (natural language interface)
- Python FastMCP Server (protocol translator) 
- C# Connector (controls ETABS/Tekla APIs)
- UBIM (Universal Building Information Model - central data storage)

**Current Goal:** 
Create a simple 2D rigid frame (2 columns + 2 sloped beams) that can be created in ETABS and synced to Tekla using commands like "Create a 40-foot rigid frame with 16-foot columns."

**Development Approach:**
I prefer to create the simplest working tool first through step-by-step tutorial (single questions/answers), then use Claude Code to complete the remaining requirements.

**Current Status:** 
Ready to start implementation. Need help with [specify: UBIM schema / Python MCP tools / C# handlers / Claude configuration].

**Question:** 
[Ask your specific implementation question here]

---

## 📚 Reference Links & Resources

### ETABS API Documentation
- Frame Object Methods: `FrameObj.AddByCoord()`, `FrameObj.SetSection()`
- Analysis Methods: `Analyze.RunAnalysis()`, `Results.FrameForce()`
- Point Methods: `PointObj.AddCartesian()`, `PointObj.GetCoordCartesian()`

### FastMCP Documentation  
- Tool Creation: `@mcp.tool()` decorator
- Server Setup: FastMCP server configuration
- Protocol: MCP JSON-RPC 2.0 specification

### Tekla API Documentation
- Beam Creation: `new Beam(startPoint, endPoint)`
- Profile Assignment: `beam.Profile.ProfileString`
- Model Operations: `model.Insert()`, `model.CommitChanges()`

## 📝 Current Progress Update

### What We've Accomplished
- ✅ **System Architecture Defined** - 4-layer approach with Claude → Python → C# → ETABS/Tekla
- ✅ **UBIM Concept Validated** - Universal model to sync data across software
- ✅ **Target Structure Selected** - 2D rigid frame (2 columns + 2 sloped beams)
- ✅ **Development Plan Created** - Phase-by-phase implementation roadmap
- ✅ **Researched Existing Solutions** - Analyzed Speckle, Bentley iTwin, PDF-to-CAD tools

### Currently Working On
- 🔄 **C# Connector Setup** - Creating the ETABS API bridge from existing GitHub code
- 🔄 **Development Environment** - Visual Studio vs VS Code decision, repository structure
- 🔄 **Testing Strategy** - MCP Inspector setup for debugging

### Next Steps
1. **Complete C# Project Setup** - Leverage existing ETABSFastMCP repository
2. **Create First Tool** - `create_rigid_frame()` with ETABS integration
3. **Test with MCP Inspector** - Validate tool communication
4. **Add Python MCP Layer** - Connect Claude to C# connector

---

*This documentation represents the complete vision and current status of the ETABS FastMCP project. Use it to maintain context across chat sessions and as a reference for implementation.*