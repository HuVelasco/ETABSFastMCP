#!/usr/bin/env python3
"""
Mock Test Demo - ETABS FastMCP Server
Demonstrates the new batch operations without requiring ETABS
"""

import asyncio
import json
from typing import Dict, Any, List

# Mock responses for demonstration
class MockETABSConnector:
    """Mock connector that simulates ETABS responses"""
    
    def __init__(self):
        self.connected = False
        self.points = {}
        self.frames = {}
        self.point_counter = 0
        self.frame_counter = 0
    
    async def send_command(self, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Simulate ETABS connector responses"""
        parameters = parameters or {}
        
        if action == "connect":
            self.connected = True
            return {
                "success": True,
                "data": {
                    "message": "Connected to ETABS (mock mode)",
                    "method": "mock",
                    "connected": True
                }
            }
        
        elif action == "create_blank_model":
            return {
                "success": True,
                "data": {
                    "message": "Mock blank model created successfully",
                    "units": "kN_m_C"
                }
            }
        
        elif action == "create_point":
            name = parameters.get("name", f"P{self.point_counter + 1}")
            coords = parameters.get("coordinates", {"x": 0, "y": 0, "z": 0})
            restraints = parameters.get("restraints", {})
            
            self.points[name] = {
                "name": name,
                "coordinates": coords,
                "restraints": restraints
            }
            self.point_counter += 1
            
            return {
                "success": True,
                "data": {
                    "name": name,
                    "coordinates": coords,
                    "message": f"Mock point {name} created successfully"
                }
            }
        
        elif action == "list_points":
            points_list = []
            for name, point_data in self.points.items():
                points_list.append({
                    "name": name,
                    "type": "Point",
                    "properties": {
                        "coordinates": point_data["coordinates"],
                        "restraints": point_data.get("restraints", {})
                    }
                })
            
            return {
                "success": True,
                "data": {
                    "count": len(points_list),
                    "points": points_list
                }
            }
        
        elif action == "create_frame":
            name = parameters.get("name", f"F{self.frame_counter + 1}")
            start_point = parameters.get("startPoint", {"x": 0, "y": 0, "z": 0})
            end_point = parameters.get("endPoint", {"x": 0, "y": 0, "z": 0})
            section = parameters.get("section", "Default")
            
            # Calculate length
            dx = end_point["x"] - start_point["x"]
            dy = end_point["y"] - start_point["y"] 
            dz = end_point["z"] - start_point["z"]
            length = (dx**2 + dy**2 + dz**2)**0.5
            
            self.frames[name] = {
                "name": name,
                "startPoint": start_point,
                "endPoint": end_point,
                "section": section,
                "length": length
            }
            self.frame_counter += 1
            
            return {
                "success": True,
                "data": {
                    "name": name,
                    "startPoint": start_point,
                    "endPoint": end_point,
                    "section": section,
                    "length": length,
                    "message": f"Mock frame {name} created successfully"
                }
            }
        
        elif action == "list_frames":
            frames_list = []
            for name, frame_data in self.frames.items():
                frames_list.append({
                    "name": name,
                    "type": "Frame", 
                    "properties": {
                        "startPoint": frame_data["startPoint"],
                        "endPoint": frame_data["endPoint"],
                        "section": frame_data.get("section", "Default"),
                        "length": frame_data.get("length", 0)
                    }
                })
            
            return {
                "success": True,
                "data": {
                    "count": len(frames_list),
                    "frames": frames_list
                }
            }
        
        elif action == "save_model":
            return {
                "success": True,
                "data": {
                    "message": "Mock model saved successfully",
                    "path": parameters.get("filePath", "mock_model.edb")
                }
            }
        
        elif action == "disconnect":
            self.connected = False
            return {
                "success": True,
                "data": {
                    "message": "Disconnected from ETABS (mock mode)",
                    "exitedApplication": parameters.get("exitApplication", False)
                }
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown mock command: {action}"
            }

# Mock MCP tools
mock_connector = MockETABSConnector()

async def create_points_batch(points: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mock batch point creation"""
    results = []
    successful_points = []
    failed_points = []
    
    for point_def in points:
        try:
            name = point_def.get("name")
            x = point_def.get("x", 0.0)
            y = point_def.get("y", 0.0)
            z = point_def.get("z", 0.0)
            restraints = point_def.get("restraints")
            
            result = await mock_connector.send_command("create_point", {
                "name": name,
                "coordinates": {"x": x, "y": y, "z": z},
                "restraints": restraints
            })
            results.append(result)
            
            if result.get("success", False):
                successful_points.append(name or "unnamed")
            else:
                failed_points.append({"name": name, "error": result.get("error", "Unknown error")})
                
        except Exception as e:
            failed_points.append({"name": point_def.get("name", "unknown"), "error": str(e)})
    
    return {
        "success": len(failed_points) == 0,
        "total_points": len(points),
        "successful_count": len(successful_points),
        "failed_count": len(failed_points),
        "successful_points": successful_points,
        "failed_points": failed_points,
        "detailed_results": results
    }

async def create_frames_by_pattern(
    start_pattern: str = "A",
    end_pattern: str = "B", 
    section: str = None,
    material: str = None
) -> Dict[str, Any]:
    """Mock pattern-based frame creation"""
    
    # Get all points
    points_result = await mock_connector.send_command("list_points")
    if not points_result.get("success", False):
        return {"success": False, "error": "Failed to get points from model"}
    
    points_data = points_result.get("data", {})
    all_points = points_data.get("points", [])
    
    # Separate points by pattern
    start_points = {}
    end_points = {}
    
    for point in all_points:
        point_name = point.get("name", "")
        if point_name.startswith(start_pattern):
            suffix = point_name[len(start_pattern):]
            start_points[suffix] = point
        elif point_name.startswith(end_pattern):
            suffix = point_name[len(end_pattern):]
            end_points[suffix] = point
    
    # Find matching pairs and create frames
    successful_frames = []
    failed_frames = []
    
    for suffix in start_points:
        if suffix in end_points:
            start_point = start_points[suffix]
            end_point = end_points[suffix]
            
            start_coords = start_point["properties"]["coordinates"]
            end_coords = end_point["properties"]["coordinates"]
            
            frame_name = f"{start_point['name']}-{end_point['name']}"
            
            try:
                result = await mock_connector.send_command("create_frame", {
                    "name": frame_name,
                    "startPoint": start_coords,
                    "endPoint": end_coords,
                    "section": section,
                    "material": material
                })
                
                if result.get("success", False):
                    successful_frames.append(frame_name)
                else:
                    failed_frames.append({"name": frame_name, "error": result.get("error", "Unknown error")})
                    
            except Exception as e:
                failed_frames.append({"name": frame_name, "error": str(e)})
        else:
            start_name = start_points[suffix]["name"]
            expected_end = f"{end_pattern}{suffix}"
            failed_frames.append({
                "name": f"{start_name}-{expected_end}",
                "error": f"No matching end point {expected_end} found"
            })
    
    return {
        "success": len(failed_frames) == 0,
        "start_pattern": start_pattern,
        "end_pattern": end_pattern,
        "pairs_found": len(start_points),
        "successful_count": len(successful_frames),
        "failed_count": len(failed_frames),
        "successful_frames": successful_frames,
        "failed_frames": failed_frames,
        "section_used": section or "Default",
        "material_used": material or "Default"
    }

async def run_mock_demo():
    """Run the mock demonstration"""
    
    print("ETABS FastMCP Server - Mock Demo")
    print("=" * 50)
    print("This demo shows the new batch operations without requiring ETABS")
    print()
    
    try:
        # 1. Connect
        print("1. Connecting to ETABS (mock)...")
        result = await mock_connector.send_command("connect")
        print(f"SUCCESS: {result['data']['message']}")
        
        # 2. Create model
        print("\n2. Creating blank model...")
        result = await mock_connector.send_command("create_blank_model")
        print(f"SUCCESS: {result['data']['message']}")
        
        # 3. Batch point creation
        print("\n3. Creating points in batch...")
        
        test_points = [
            {"name": "A1", "x": 0, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "A2", "x": 8, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "A3", "x": 16, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "B1", "x": 0, "y": 0, "z": 4, "restraints": {}},
            {"name": "B2", "x": 8, "y": 0, "z": 4, "restraints": {}},
            {"name": "B3", "x": 16, "y": 0, "z": 4, "restraints": {}},
        ]
        
        result = await create_points_batch(test_points)
        print(f"✅ Created {result['successful_count']}/{result['total_points']} points")
        print(f"📍 Points: {', '.join(result['successful_points'])}")
        
        # 4. List points to verify
        print("\n4. ✅ Verifying points...")
        points_result = await mock_connector.send_command("list_points")
        for point in points_result["data"]["points"]:
            coords = point["properties"]["coordinates"]
            restraints = point["properties"]["restraints"]
            restraint_info = ", ".join([k for k, v in restraints.items() if v])
            restraint_text = f" (restraints: {restraint_info})" if restraint_info else ""
            print(f"   • {point['name']}: ({coords['x']}, {coords['y']}, {coords['z']}){restraint_text}")
        
        # 5. Pattern-based frame creation
        print("\n5. 🏗️ Creating frames by pattern (A->B)...")
        result = await create_frames_by_pattern(
            start_pattern="A",
            end_pattern="B",
            section="W14X90",
            material="A992"
        )
        
        print(f"✅ Created {result['successful_count']} frames")
        print(f"🏗️ Frames: {', '.join(result['successful_frames'])}")
        print(f"📏 Section: {result['section_used']}")
        
        # 6. List frames to verify
        print("\n6. 🏗️ Verifying frames...")
        frames_result = await mock_connector.send_command("list_frames")
        for frame in frames_result["data"]["frames"]:
            section = frame["properties"]["section"]
            length = frame["properties"]["length"]
            start = frame["properties"]["startPoint"]
            end = frame["properties"]["endPoint"]
            print(f"   • {frame['name']}: {section} (L={length:.1f}m)")
            print(f"     From ({start['x']}, {start['y']}, {start['z']}) to ({end['x']}, {end['y']}, {end['z']})")
        
        # 7. Save model
        print("\n7. 💾 Saving model...")
        result = await mock_connector.send_command("save_model", {"filePath": "demo_model.edb"})
        print(f"✅ {result['data']['message']}")
        
        print("\n🎉 Mock demo completed successfully!")
        
        # Show Claude examples
        print("\n" + "=" * 60)
        print("🤖 CLAUDE DESKTOP USAGE EXAMPLES")
        print("=" * 60)
        
        examples = [
            "Create the following points: A1 at (0,0,0), A2 at (10,0,0), B1 at (0,0,4), B2 at (10,0,4) with base restraints on A points",
            "Create frames connecting all A points to B points using W14X90 sections",
            "Show me all structural elements in the model with their properties",
            "Create a 5-bay building frame with columns every 8 meters and W21X50 beams"
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"\n{i}. 💬 \"{example}\"")
        
        print(f"\n{'=' * 60}")
        print("✨ The server will automatically:")
        print("   • Parse your natural language request")
        print("   • Create the appropriate point and frame definitions")
        print("   • Use batch operations for efficiency")
        print("   • Match points by naming patterns")
        print("   • Provide detailed feedback on success/failures")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting ETABS FastMCP Mock Demo...")
    print("This demonstrates the new batch operations functionality")
    print()
    
    asyncio.run(run_mock_demo())