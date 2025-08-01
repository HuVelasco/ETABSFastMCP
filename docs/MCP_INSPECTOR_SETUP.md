# 🔍 MCP Inspector Setup Guide
**Authors: Hugo & BIM Master**

## What is the MCP Inspector?

The MCP Inspector is a powerful debugging and testing tool that lets you:
- ✅ Test your MCP server without Claude Desktop
- ✅ Inspect all available tools and their parameters
- ✅ Call tools directly and see responses
- ✅ Debug issues before deploying to Claude Desktop

## 🚀 Quick Setup

### 1. Install Node.js (Required for Inspector)

**Download**: https://nodejs.org/en/download/
- Install the LTS version
- Verify: `node --version` and `npm --version`

### 2. Install MCP Inspector

```bash
# Install globally
npm install -g @modelcontextprotocol/inspector

# Verify installation
npx @modelcontextprotocol/inspector --help
```

### 3. Prepare Your Environment

**Run our setup script first:**
```bash
cd C:\Users\hugov\ClaudeProjects\2503_TeklaMCP\TeklaMCP.HttpServer\ETABSFastMCP
setup_environment.bat
```

This will:
- Create virtual environment
- Install Python dependencies
- Build C# connector
- Test the system

## 🧪 Testing with Inspector

### Method 1: Direct Python Server Testing

```bash
# 1. Activate virtual environment
cd C:\Users\hugov\ClaudeProjects\2503_TeklaMCP\TeklaMCP.HttpServer\ETABSFastMCP
venv\Scripts\activate.bat

# 2. Launch inspector with Python server
npx @modelcontextprotocol/inspector python python-server/etabs_server.py
```

### Method 2: Using UV (Recommended approach from your example)

```bash
# 1. Install UV (if not already installed)
pip install uv

# 2. Navigate to project
cd C:\Users\hugov\ClaudeProjects\2503_TeklaMCP\TeklaMCP.HttpServer\ETABSFastMCP

# 3. Initialize with UV
uv init

# 4. Create virtual environment
uv venv

# 5. Activate environment
# On Windows:
.venv\Scripts\activate.bat
# On Unix/Mac:
# source .venv/bin/activate

# 6. Install dependencies with UV
uv add mcp asyncio pydantic typing-extensions

# 7. Launch inspector
npx @modelcontextprotocol/inspector uv run python-server/etabs_server.py
```

## 🌐 Using the Inspector UI

### 1. Start the Inspector

When you run the inspector command, you'll see:
```
MCP Inspector running at http://localhost:3000
Inspector Proxy Address: http://localhost:3001
```

### 2. Open the Inspector

- Click on the `http://localhost:3000` link
- The inspector will open in your browser

### 3. Configure Connection

In the Inspector UI:

1. **Server Configuration**:
   - **Command**: `python`
   - **Args**: `["python-server/etabs_server.py"]`
   - **Environment**: `{"PYTHONPATH": "python-server"}`

2. **Inspector Proxy Address**:
   - Use: `http://localhost:3001`

### 4. Test Your Tools

The inspector will show all available tools:

**Connection Tools:**
- `connect_to_etabs`
- `create_blank_model`
- `get_connection_status`

**Point Tools:**
- `create_point`
- `create_points_batch`
- `list_points`
- `modify_point`
- `delete_point`

**Frame Tools:**
- `create_frame`
- `create_frames_by_pattern`
- `list_frames`
- `modify_frame`
- `delete_frame`

**Model Tools:**
- `save_model`
- `health_check`

## 🎯 Step-by-Step Testing Workflow

### Test 1: Health Check
1. **Click** on `health_check` tool
2. **Click** "Call Tool"
3. **Expected Response**:
   ```json
   {
     "success": true,
     "server": "running",
     "connector_process": "running",
     "connector_responsive": true
   }
   ```

### Test 2: Connect to ETABS
1. **Click** on `connect_to_etabs` tool
2. **Set Parameters**:
   - `attach_to_existing`: `true` or `false`
3. **Click** "Call Tool"
4. **Expected Response**:
   ```json
   {
     "success": true,
     "data": {
       "message": "Connected to ETABS successfully",
       "method": "new",
       "connected": true
     }
   }
   ```

### Test 3: Create Blank Model
1. **Click** on `create_blank_model` tool
2. **Click** "Call Tool"
3. **Expected Response**:
   ```json
   {
     "success": true,
     "data": {
       "message": "Blank model created successfully",
       "units": "kN_m_C"
     }
   }
   ```

### Test 4: Batch Point Creation
1. **Click** on `create_points_batch` tool
2. **Set Parameters**:
   ```json
   {
     "points": [
       {"name": "A1", "x": 0, "y": 0, "z": 0, "restraints": {"UZ": true}},
       {"name": "A2", "x": 10, "y": 0, "z": 0, "restraints": {"UZ": true}},
       {"name": "B1", "x": 0, "y": 0, "z": 4},
       {"name": "B2", "x": 10, "y": 0, "z": 4}
     ]
   }
   ```
3. **Click** "Call Tool"
4. **Check Response** for successful point creation

### Test 5: Pattern-Based Frame Creation
1. **Click** on `create_frames_by_pattern` tool
2. **Set Parameters**:
   ```json
   {
     "start_pattern": "A",
     "end_pattern": "B",
     "section": "W14X90",
     "material": "A992"
   }
   ```
3. **Click** "Call Tool"
4. **Check Response** for successful frame creation

## 🐛 Troubleshooting

### Common Issues

**"Inspector won't start"**
```bash
# Check Node.js version
node --version  # Should be 16+ 

# Reinstall inspector
npm uninstall -g @modelcontextprotocol/inspector
npm install -g @modelcontextprotocol/inspector
```

**"Python server not found"**
```bash
# Make sure you're in the right directory
cd C:\Users\hugov\ClaudeProjects\2503_TeklaMCP\TeklaMCP.HttpServer\ETABSFastMCP

# Check virtual environment
venv\Scripts\activate.bat
python --version

# Test server directly
python python-server/etabs_server.py
```

**"Connector process not starting"**
1. Build the C# connector first:
   ```bash
   setup_environment.bat
   ```
2. Or build manually in Visual Studio
3. Check that ETABS is installed

**"Tools not showing up in inspector"**
1. Check that all `@mcp.tool()` decorators are present
2. Verify no Python syntax errors
3. Test server in isolation first

## 📋 Inspector Checklist

Before using Claude Desktop, verify in Inspector:

- ✅ Health check passes
- ✅ ETABS connection works
- ✅ Point creation succeeds
- ✅ Frame creation succeeds
- ✅ Batch operations work
- ✅ Error handling works (try invalid inputs)
- ✅ All tools are discoverable

## 🔗 Integration with Claude Desktop

Once Inspector testing passes:

1. **Copy configuration** from `config/claude_desktop_config.json`
2. **Add to Claude Desktop** settings
3. **Restart Claude Desktop**
4. **Test with natural language** commands

**Example Claude commands to try:**
- "Connect to ETABS and create a new blank model"
- "Create points A1, A2, B1, B2 in a rectangular pattern"
- "Create frames connecting A points to B points with W14X90 sections"

---

**The Inspector is your best friend for debugging MCP servers! 🚀**

*Test everything in the Inspector before moving to Claude Desktop.*