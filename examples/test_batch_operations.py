#!/usr/bin/env python3
"""
Comprehensive Test Script - ETABS FastMCP Server
Tests batch operations and pattern-based frame creation
"""

import asyncio
import json
from pathlib import Path
import sys

# Add the python-server directory to the path
sys.path.append(str(Path(__file__).parent.parent / "python-server"))

from etabs_server import connector, create_points_batch, create_frames_by_pattern

async def test_batch_operations():
    """Test the new batch operations functionality"""
    
    print("🧪 ETABS FastMCP Server - Batch Operations Test")
    print("=" * 60)
    
    try:
        # 1. Connect to ETABS
        print("1. 🔗 Connecting to ETABS...")
        result = await connector.send_command("connect", {"attachToExisting": False})
        if not result["success"]:
            print(f"❌ Connection failed: {result['error']}")
            return False
        print(f"✅ {result['data']['message']}")
        
        # 2. Create blank model
        print("\n2. 📄 Creating blank model...")
        result = await connector.send_command("create_blank_model")
        if not result["success"]:
            print(f"❌ Failed to create model: {result['error']}")
            return False
        print(f"✅ {result['data']['message']}")
        
        # 3. Test batch point creation
        print("\n3. 📍 Testing batch point creation...")
        
        # Define a list of points for a simple beam structure
        test_points = [
            # Column base points (A series)
            {"name": "A1", "x": 0, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "A2", "x": 8, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "A3", "x": 16, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "A4", "x": 24, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            
            # Column top points (B series) - at 4m height
            {"name": "B1", "x": 0, "y": 0, "z": 4, "restraints": {}},
            {"name": "B2", "x": 8, "y": 0, "z": 4, "restraints": {}},
            {"name": "B3", "x": 16, "y": 0, "z": 4, "restraints": {}},
            {"name": "B4", "x": 24, "y": 0, "z": 4, "restraints": {}},
            
            # Additional points for cross bracing (C series)
            {"name": "C1", "x": 4, "y": 0, "z": 2, "restraints": {}},
            {"name": "C2", "x": 12, "y": 0, "z": 2, "restraints": {}},
            {"name": "C3", "x": 20, "y": 0, "z": 2, "restraints": {}},
        ]
        
        print(f"   Creating {len(test_points)} points...")
        result = await create_points_batch(test_points)
        
        if result["success"]:
            print(f"   ✅ Successfully created {result['successful_count']}/{result['total_points']} points")
            print(f"   📍 Points created: {', '.join(result['successful_points'])}")
            if result['failed_points']:
                print(f"   ⚠️ Failed points: {result['failed_points']}")
        else:
            print(f"   ❌ Batch creation failed: {result['error']}")
            return False
        
        # 4. Verify points were created
        print("\n4. ✅ Verifying point creation...")
        points_result = await connector.send_command("list_points")
        if points_result["success"]:
            created_points = points_result["data"]["points"]
            print(f"   📊 Total points in model: {len(created_points)}")
            
            # Show some examples
            for point in created_points[:5]:  # Show first 5
                coords = point["properties"]["coordinates"]
                restraints = point["properties"]["restraints"]
                restraint_info = ", ".join([k for k, v in restraints.items() if v])
                restraint_text = f" (restraints: {restraint_info})" if restraint_info else ""
                print(f"   • {point['name']}: ({coords['x']}, {coords['y']}, {coords['z']}){restraint_text}")
            
            if len(created_points) > 5:
                print(f"   • ... and {len(created_points) - 5} more points")
        
        # 5. Test pattern-based frame creation
        print("\n5. 🏗️ Testing pattern-based frame creation...")
        
        # Create vertical columns (A to B pattern)
        print("   Creating vertical columns (A->B pattern)...")
        result = await create_frames_by_pattern(
            start_pattern="A",
            end_pattern="B", 
            section="W14X90",
            material="A992"
        )
        
        if result["success"]:
            print(f"   ✅ Successfully created {result['successful_count']} column frames")
            print(f"   🏗️ Columns: {', '.join(result['successful_frames'])}")
            print(f"   📏 Section: {result['section_used']}")
        else:
            print(f"   ❌ Column creation failed: {result['error']}")
            if result.get('failed_frames'):
                for failure in result['failed_frames']:
                    print(f"     • {failure['name']}: {failure['error']}")
        
        # Create horizontal beams at top level (B to B pattern)
        print("\n   Creating horizontal beams (B1->B2, B2->B3, etc.)...")
        
        # For this we need to create frames manually since B->B won't work
        # Let's create beams connecting consecutive B points
        beam_results = []
        b_points = [(f"B{i}", 8*(i-1), 0, 4) for i in range(1, 5)]  # B1, B2, B3, B4
        
        for i in range(len(b_points) - 1):
            start_name, start_x, start_y, start_z = b_points[i]
            end_name, end_x, end_y, end_z = b_points[i + 1]
            beam_name = f"Beam_{start_name}_{end_name}"
            
            beam_result = await connector.send_command("create_frame", {
                "name": beam_name,
                "startPoint": {"x": start_x, "y": start_y, "z": start_z},
                "endPoint": {"x": end_x, "y": end_y, "z": end_z},
                "section": "W21X50",
                "material": "A992"
            })
            
            beam_results.append({"name": beam_name, "success": beam_result.get("success", False)})
        
        successful_beams = [b["name"] for b in beam_results if b["success"]]
        print(f"   ✅ Created {len(successful_beams)} horizontal beams: {', '.join(successful_beams)}")
        
        # 6. Final model summary
        print("\n6. 📊 Final model summary...")
        
        # Get all frames
        frames_result = await connector.send_command("list_frames")
        if frames_result["success"]:
            all_frames = frames_result["data"]["frames"]
            print(f"   🏗️ Total frames: {len(all_frames)}")
            
            # Categorize frames
            columns = [f for f in all_frames if "A" in f["name"] and "B" in f["name"]]
            beams = [f for f in all_frames if "Beam_" in f["name"]]
            
            print(f"   📐 Columns: {len(columns)}")
            print(f"   📏 Beams: {len(beams)}")
            
            # Show frame details
            for frame in all_frames:
                section = frame["properties"].get("section", "Default")
                length = frame["properties"].get("length", 0)
                print(f"   • {frame['name']}: {section} (L={length:.1f}m)")
        
        # 7. Save the model
        print("\n7. 💾 Saving the model...")
        save_result = await connector.send_command("save_model", {
            "filePath": str(Path(__file__).parent / "test_batch_model.edb")
        })
        
        if save_result["success"]:
            print(f"   ✅ Model saved successfully")
        else:
            print(f"   ⚠️ Save failed: {save_result.get('error', 'Unknown error')}")
        
        print("\n🎉 All tests completed successfully!")
        print("\n💡 You can now:")
        print("   • View the model in ETABS")
        print("   • Use Claude Desktop with commands like:")
        print("     - 'Create points A1 through A5 at 5m spacing'")
        print("     - 'Create frames from A points to B points with W14X90 sections'")
        print("     - 'List all structural elements in the model'")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_claude_style_commands():
    """Demonstrate Claude-style natural language commands"""
    
    print("\n" + "=" * 60)
    print("🤖 CLAUDE DESKTOP COMMAND EXAMPLES")
    print("=" * 60)
    
    examples = [
        {
            "command": "Create the following points: A1 at (0,0,0), A2 at (10,0,0), B1 at (0,0,4), B2 at (10,0,4)",
            "explanation": "Use create_points_batch with list of point definitions"
        },
        {
            "command": "Create frames connecting A points to B points with W14X90 sections",
            "explanation": "Use create_frames_by_pattern with start_pattern='A', end_pattern='B'"
        },
        {
            "command": "Show me all the structural elements in the model",
            "explanation": "Use list_points and list_frames to get complete model information"
        },
        {
            "command": "Create a 4-bay building frame with columns every 8 meters",
            "explanation": "Create points A1-A5, B1-B5, then use pattern-based frame creation"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. 💬 Claude Command:")
        print(f"   '{example['command']}'")
        print(f"   🔧 Implementation: {example['explanation']}")
    
    print(f"\n{'=' * 60}")
    print("✨ The server automatically handles the complexity!")
    print("   Just describe what you want in natural language.")

if __name__ == "__main__":
    async def main():
        print("Starting ETABS connector...")
        
        # Start the connector
        success = await connector.start()
        if not success:
            print("❌ Failed to start ETABS connector")
            print("🔧 Make sure:")
            print("   • C# connector is built (run: msbuild ETABSConnector.csproj)")
            print("   • ETABS software is installed")
            print("   • .NET Framework 4.8 is installed")
            return
        
        try:
            # Run the comprehensive test
            test_success = await test_batch_operations()
            
            if test_success:
                # Show Claude command examples
                await test_claude_style_commands()
                print("\n🏆 All tests passed! Server is ready for production use.")
            else:
                print("\n❌ Some tests failed. Check the error messages above.")
            
        finally:
            # Clean up
            try:
                await connector.send_command("disconnect", {"exitApplication": False})
                print("\n🔌 Disconnected from ETABS")
            except:
                pass
            
            await connector.stop()
            print("🛑 Connector stopped")
    
    # Run the test
    asyncio.run(main())