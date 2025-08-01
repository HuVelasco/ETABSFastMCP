#!/usr/bin/env python3
"""
Basic Usage Example - ETABS FastMCP Server
Demonstrates common operations through direct API calls
"""

import asyncio
import json
from pathlib import Path
import sys

# Add the python-server directory to the path
sys.path.append(str(Path(__file__).parent.parent / "python-server"))

from etabs_server import connector

async def example_basic_model():
    """Create a basic structural model example"""
    
    print("🏗️ ETABS FastMCP Server Example")
    print("=" * 50)
    
    try:
        # 1. Connect to ETABS
        print("1. Connecting to ETABS...")
        result = await connector.send_command("connect", {"attachToExisting": False})
        if not result["success"]:
            print(f"❌ Connection failed: {result['error']}")
            return
        print(f"✅ {result['data']['message']}")
        
        # 2. Create blank model
        print("\n2. Creating blank model...")
        result = await connector.send_command("create_blank_model")
        if not result["success"]:
            print(f"❌ Failed to create model: {result['error']}")
            return
        print(f"✅ {result['data']['message']}")
        
        # 3. Create corner points for a simple frame
        print("\n3. Creating structural points...")
        points = [
            {"name": "A", "coords": (0, 0, 0), "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "B", "coords": (10, 0, 0), "restraints": {"UZ": True}},
            {"name": "C", "coords": (10, 10, 0), "restraints": {"UZ": True}},
            {"name": "D", "coords": (0, 10, 0), "restraints": {"UZ": True}},
        ]
        
        for point in points:
            result = await connector.send_command("create_point", {
                "name": point["name"],
                "coordinates": {"x": point["coords"][0], "y": point["coords"][1], "z": point["coords"][2]},
                "restraints": point["restraints"]
            })
            
            if result["success"]:
                print(f"  ✅ Created point {point['name']} at {point['coords']}")
            else:
                print(f"  ❌ Failed to create point {point['name']}: {result['error']}")
        
        # 4. Create frame elements
        print("\n4. Creating frame elements...")
        frames = [
            {"name": "AB", "start": "A", "end": "B", "coords": [(0,0,0), (10,0,0)]},
            {"name": "BC", "start": "B", "end": "C", "coords": [(10,0,0), (10,10,0)]},
            {"name": "CD", "start": "C", "end": "D", "coords": [(10,10,0), (0,10,0)]},
            {"name": "DA", "start": "D", "end": "A", "coords": [(0,10,0), (0,0,0)]},
        ]
        
        for frame in frames:
            start_coords = frame["coords"][0]
            end_coords = frame["coords"][1]
            
            result = await connector.send_command("create_frame", {
                "name": frame["name"],
                "startPoint": {"x": start_coords[0], "y": start_coords[1], "z": start_coords[2]},
                "endPoint": {"x": end_coords[0], "y": end_coords[1], "z": end_coords[2]},
                "section": "W14X90"
            })
            
            if result["success"]:
                print(f"  ✅ Created frame {frame['name']} from {frame['start']} to {frame['end']}")
            else:
                print(f"  ❌ Failed to create frame {frame['name']}: {result['error']}")
        
        # 5. List all objects in the model
        print("\n5. Listing model objects...")
        
        # List points
        result = await connector.send_command("list_points")
        if result["success"]:
            print(f"  📍 Total points: {result['data']['count']}")
            for point in result['data']['points']:
                coords = point['properties']['coordinates']
                print(f"    - {point['name']}: ({coords['x']}, {coords['y']}, {coords['z']})")
        
        # List frames
        result = await connector.send_command("list_frames")
        if result["success"]:
            print(f"  🏗️ Total frames: {result['data']['count']}")
            for frame in result['data']['frames']:
                section = frame['properties'].get('section', 'Default')
                length = frame['properties'].get('length', 0)
                print(f"    - {frame['name']}: {section} (Length: {length:.2f}m)")
        
        # 6. Get system status
        print("\n6. System status...")
        result = await connector.send_command("status")
        if result["success"]:
            status = result['data']
            print(f"  🔗 Connected: {status['connected']}")
            if status.get('modelPath'):
                print(f"  📁 Model: {status['modelPath']}")
        
        print("\n🎉 Example completed successfully!")
        print("\nYou can now:")
        print("- View the model in ETABS")
        print("- Use Claude Desktop to interact with the model")
        print("- Try commands like 'List all frames in the model'")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
    
    finally:
        # Clean up
        try:
            await connector.send_command("disconnect", {"exitApplication": False})
            print("\n🔌 Disconnected from ETABS")
        except:
            pass

async def example_claude_commands():
    """Show example commands for Claude Desktop"""
    
    print("\n" + "=" * 60)
    print("📝 EXAMPLE CLAUDE DESKTOP COMMANDS")
    print("=" * 60)
    
    commands = [
        {
            "category": "🔗 Connection",
            "examples": [
                "Connect to ETABS and create a new blank model",
                "Check the ETABS connection status",
                "Disconnect from ETABS"
            ]
        },
        {
            "category": "📍 Points",
            "examples": [
                "Create a point at coordinates (5, 5, 0) with UZ restraint",
                "List all points in the model",
                "Get information about point A",
                "Modify point B to have full restraints",
                "Delete point C from the model"
            ]
        },
        {
            "category": "🏗️ Frames", 
            "examples": [
                "Create a frame from (0,0,0) to (10,0,0) with W14X90 section",
                "List all frame elements in the model",
                "Get properties of frame AB",
                "Change frame BC to use W21X50 section",
                "Delete frame CD from the model"
            ]
        },
        {
            "category": "🏢 Complex Structures",
            "examples": [
                "Create a 4-story building frame with 3 bays in each direction",
                "Build a simple truss with 5 panels",
                "Create a moment frame with rigid connections",
                "Generate a braced frame system"
            ]
        },
        {
            "category": "💾 Model Management",
            "examples": [
                "Save the current model as 'my_building.edb'",
                "Check the model for any errors",
                "Show me a summary of all structural elements"
            ]
        }
    ]
    
    for cmd_group in commands:
        print(f"\n{cmd_group['category']}")
        print("-" * 40)
        for example in cmd_group['examples']:
            print(f"  • {example}")
    
    print(f"\n{'=' * 60}")
    print("💡 TIP: Use natural language with Claude Desktop!")
    print("   Just describe what you want to build and Claude will")
    print("   convert it to the appropriate ETABS commands.")
    print("=" * 60)

if __name__ == "__main__":
    async def main():
        # Start the connector
        success = await connector.start()
        if not success:
            print("❌ Failed to start ETABS connector")
            print("Make sure the C# connector is built and ETABS is installed")
            return
        
        try:
            # Run the basic example
            await example_basic_model()
            
            # Show Claude command examples
            await example_claude_commands()
            
        finally:
            # Stop the connector
            await connector.stop()
    
    # Run the example
    asyncio.run(main())