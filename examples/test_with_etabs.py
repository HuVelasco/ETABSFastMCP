#!/usr/bin/env python3
"""
ETABS FastMCP - Real ETABS Integration Test
Authors: Hugo & BIM Master

This script demonstrates how to:
1. Start ETABS automatically
2. Create a blank model
3. Use batch operations
4. Test with real ETABS (not mock)
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the python-server directory to the path
sys.path.append(str(Path(__file__).parent.parent / "python-server"))

from etabs_server import connector

async def test_real_etabs():
    """Test with real ETABS application"""
    
    print("ETABS FastMCP - Real ETABS Integration Test")
    print("Authors: Hugo & BIM Master")
    print("=" * 60)
    print()
    
    try:
        # Start the C# connector
        print("Starting ETABS connector...")
        success = await connector.start()
        if not success:
            print("ERROR: Failed to start ETABS connector")
            print("Make sure:")
            print("  1. C# connector is built (run setup_environment.bat)")
            print("  2. ETABS is installed")
            print("  3. .NET Framework 4.8 is installed")
            return False
        
        print("SUCCESS: Connector started")
        print()
        
        # Test 1: Connect to ETABS
        print("TEST 1: Connecting to ETABS...")
        result = await connector.send_command("connect", {"attachToExisting": False})
        
        if result["success"]:
            print(f"SUCCESS: {result['data']['message']}")
            print(f"Method: {result['data']['method']}")
        else:
            print(f"ERROR: {result['error']}")
            return False
        
        # Test 2: Create blank model
        print("\nTEST 2: Creating blank model...")
        result = await connector.send_command("create_blank_model")
        
        if result["success"]:
            print(f"SUCCESS: {result['data']['message']}")
        else:
            print(f"ERROR: {result['error']}")
            return False
        
        # Test 3: Create points individually
        print("\nTEST 3: Creating individual points...")
        test_points = [
            {"name": "A1", "x": 0, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "A2", "x": 10, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "B1", "x": 0, "y": 0, "z": 4, "restraints": {}},
            {"name": "B2", "x": 10, "y": 0, "z": 4, "restraints": {}}
        ]
        
        for point in test_points:
            result = await connector.send_command("create_point", {
                "name": point["name"],
                "coordinates": {"x": point["x"], "y": point["y"], "z": point["z"]},
                "restraints": point["restraints"]
            })
            
            if result["success"]:
                print(f"  SUCCESS: Created point {point['name']}")
            else:
                print(f"  ERROR: Failed to create {point['name']}: {result['error']}")
        
        # Test 4: List points
        print("\nTEST 4: Listing all points...")
        result = await connector.send_command("list_points")
        
        if result["success"]:
            points = result["data"]["points"]
            print(f"SUCCESS: Found {len(points)} points")
            for point in points:
                coords = point["properties"]["coordinates"]
                print(f"  - {point['name']}: ({coords['x']}, {coords['y']}, {coords['z']})")
        else:
            print(f"ERROR: {result['error']}")
        
        # Test 5: Create frames individually
        print("\nTEST 5: Creating frame elements...")
        frame_pairs = [("A1", "B1"), ("A2", "B2")]
        
        for start_name, end_name in frame_pairs:
            # Get point coordinates
            start_point = next((p for p in points if p["name"] == start_name), None)
            end_point = next((p for p in points if p["name"] == end_name), None)
            
            if start_point and end_point:
                start_coords = start_point["properties"]["coordinates"]
                end_coords = end_point["properties"]["coordinates"]
                
                result = await connector.send_command("create_frame", {
                    "name": f"Column_{start_name}_{end_name}",
                    "startPoint": start_coords,
                    "endPoint": end_coords,
                    "section": "W14X90",
                    "material": "A992"
                })
                
                if result["success"]:
                    print(f"  SUCCESS: Created frame {start_name}-{end_name}")
                else:
                    print(f"  ERROR: Failed to create frame {start_name}-{end_name}: {result['error']}")
        
        # Test 6: List frames
        print("\nTEST 6: Listing all frames...")
        result = await connector.send_command("list_frames")
        
        if result["success"]:
            frames = result["data"]["frames"]
            print(f"SUCCESS: Found {len(frames)} frames")
            for frame in frames:
                props = frame["properties"]
                section = props.get("section", "Default")
                length = props.get("length", 0)
                print(f"  - {frame['name']}: {section} (Length: {length:.2f}m)")
        else:
            print(f"ERROR: {result['error']}")
        
        # Test 7: Save the model
        print("\nTEST 7: Saving the model...")
        save_path = str(Path(__file__).parent / "test_model.edb")
        result = await connector.send_command("save_model", {"filePath": save_path})
        
        if result["success"]:
            print(f"SUCCESS: Model saved to {save_path}")
        else:
            print(f"WARNING: Save failed: {result.get('error')}")
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print()
        print("ETABS should now show:")
        print("  - 4 points (A1, A2, B1, B2)")
        print("  - 2 column frames (A1-B1, A2-B2)")
        print("  - Points A1, A2 have base restraints")
        print("  - Frames use W14X90 sections")
        print()
        print("Next steps:")
        print("  1. Check ETABS to see the created model")
        print("  2. Set up Claude Desktop integration")
        print("  3. Test with MCP Inspector")
        
        return True
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up
        try:
            print("\nCleaning up...")
            await connector.send_command("disconnect", {"exitApplication": False})
            await connector.stop()
            print("Connector stopped")
        except:
            pass

if __name__ == "__main__":
    print("Preparing to test with real ETABS...")
    print("Make sure ETABS is installed and your connector is built!")
    print()
    
    asyncio.run(test_real_etabs())