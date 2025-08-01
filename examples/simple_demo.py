#!/usr/bin/env python3
"""
Simple Demo - ETABS FastMCP Server
Shows batch operations functionality without emojis
"""

import asyncio
import json
from typing import Dict, Any, List

# Mock responses for demonstration
class MockETABSConnector:
    def __init__(self):
        self.connected = False
        self.points = {}
        self.frames = {}
    
    async def send_command(self, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        parameters = parameters or {}
        
        if action == "connect":
            return {"success": True, "data": {"message": "Connected to ETABS (mock mode)"}}
        
        elif action == "create_blank_model":
            return {"success": True, "data": {"message": "Mock blank model created"}}
        
        elif action == "create_point":
            name = parameters.get("name", f"P{len(self.points)+1}")
            coords = parameters.get("coordinates", {"x": 0, "y": 0, "z": 0})
            self.points[name] = {"coordinates": coords, "restraints": parameters.get("restraints", {})}
            return {"success": True, "data": {"name": name, "coordinates": coords}}
        
        elif action == "list_points":
            points_list = []
            for name, data in self.points.items():
                points_list.append({
                    "name": name,
                    "properties": {"coordinates": data["coordinates"], "restraints": data["restraints"]}
                })
            return {"success": True, "data": {"count": len(points_list), "points": points_list}}
        
        elif action == "create_frame":
            name = parameters.get("name", f"F{len(self.frames)+1}")
            start = parameters.get("startPoint", {"x": 0, "y": 0, "z": 0})
            end = parameters.get("endPoint", {"x": 0, "y": 0, "z": 0})
            section = parameters.get("section", "Default")
            
            # Calculate length
            dx = end["x"] - start["x"]
            dy = end["y"] - start["y"] 
            dz = end["z"] - start["z"]
            length = (dx**2 + dy**2 + dz**2)**0.5
            
            self.frames[name] = {"startPoint": start, "endPoint": end, "section": section, "length": length}
            return {"success": True, "data": {"name": name, "section": section, "length": length}}
        
        elif action == "list_frames":
            frames_list = []
            for name, data in self.frames.items():
                frames_list.append({
                    "name": name,
                    "properties": {
                        "startPoint": data["startPoint"],
                        "endPoint": data["endPoint"],
                        "section": data["section"],
                        "length": data["length"]
                    }
                })
            return {"success": True, "data": {"count": len(frames_list), "frames": frames_list}}
        
        else:
            return {"success": False, "error": f"Unknown command: {action}"}

async def create_points_batch(connector, points: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create multiple points in batch"""
    successful_points = []
    failed_points = []
    
    for point_def in points:
        try:
            result = await connector.send_command("create_point", {
                "name": point_def.get("name"),
                "coordinates": {"x": point_def.get("x", 0), "y": point_def.get("y", 0), "z": point_def.get("z", 0)},
                "restraints": point_def.get("restraints")
            })
            
            if result.get("success"):
                successful_points.append(point_def.get("name"))
            else:
                failed_points.append({"name": point_def.get("name"), "error": result.get("error")})
        except Exception as e:
            failed_points.append({"name": point_def.get("name"), "error": str(e)})
    
    return {
        "success": len(failed_points) == 0,
        "total_points": len(points),
        "successful_count": len(successful_points),
        "successful_points": successful_points,
        "failed_points": failed_points
    }

async def create_frames_by_pattern(connector, start_pattern="A", end_pattern="B", section=None):
    """Create frames by matching point name patterns"""
    
    # Get all points
    points_result = await connector.send_command("list_points")
    if not points_result.get("success"):
        return {"success": False, "error": "Failed to get points"}
    
    all_points = points_result["data"]["points"]
    
    # Separate points by pattern
    start_points = {}
    end_points = {}
    
    for point in all_points:
        point_name = point["name"]
        if point_name.startswith(start_pattern):
            suffix = point_name[len(start_pattern):]
            start_points[suffix] = point
        elif point_name.startswith(end_pattern):
            suffix = point_name[len(end_pattern):]
            end_points[suffix] = point
    
    # Create frames for matching pairs
    successful_frames = []
    failed_frames = []
    
    for suffix in start_points:
        if suffix in end_points:
            start_point = start_points[suffix]
            end_point = end_points[suffix]
            
            frame_name = f"{start_point['name']}-{end_point['name']}"
            
            result = await connector.send_command("create_frame", {
                "name": frame_name,
                "startPoint": start_point["properties"]["coordinates"],
                "endPoint": end_point["properties"]["coordinates"],
                "section": section
            })
            
            if result.get("success"):
                successful_frames.append(frame_name)
            else:
                failed_frames.append({"name": frame_name, "error": result.get("error")})
    
    return {
        "success": len(failed_frames) == 0,
        "successful_count": len(successful_frames),
        "successful_frames": successful_frames,
        "failed_frames": failed_frames,
        "section_used": section or "Default"
    }

async def main():
    print("ETABS FastMCP Server - Batch Operations Demo")
    print("=" * 50)
    print("Demonstrating the new batch functionality")
    print()
    
    connector = MockETABSConnector()
    
    try:
        # 1. Connect
        print("1. Connecting to ETABS...")
        result = await connector.send_command("connect")
        print(f"   SUCCESS: {result['data']['message']}")
        
        # 2. Create model
        print("\n2. Creating blank model...")
        result = await connector.send_command("create_blank_model")
        print(f"   SUCCESS: {result['data']['message']}")
        
        # 3. Create points in batch
        print("\n3. Creating points in batch...")
        test_points = [
            {"name": "A1", "x": 0, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "A2", "x": 8, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "A3", "x": 16, "y": 0, "z": 0, "restraints": {"UX": True, "UY": True, "UZ": True}},
            {"name": "B1", "x": 0, "y": 0, "z": 4, "restraints": {}},
            {"name": "B2", "x": 8, "y": 0, "z": 4, "restraints": {}},
            {"name": "B3", "x": 16, "y": 0, "z": 4, "restraints": {}},
        ]
        
        result = await create_points_batch(connector, test_points)
        print(f"   SUCCESS: Created {result['successful_count']}/{result['total_points']} points")
        print(f"   Points: {', '.join(result['successful_points'])}")
        
        # 4. List points
        print("\n4. Listing all points:")
        points_result = await connector.send_command("list_points")
        for point in points_result["data"]["points"]:
            coords = point["properties"]["coordinates"]
            restraints = point["properties"]["restraints"]
            restraint_info = ", ".join([k for k, v in restraints.items() if v])
            restraint_text = f" (restraints: {restraint_info})" if restraint_info else ""
            print(f"   - {point['name']}: ({coords['x']}, {coords['y']}, {coords['z']}){restraint_text}")
        
        # 5. Create frames by pattern
        print("\n5. Creating frames by pattern (A->B)...")
        result = await create_frames_by_pattern(connector, "A", "B", "W14X90")
        print(f"   SUCCESS: Created {result['successful_count']} frames")
        print(f"   Frames: {', '.join(result['successful_frames'])}")
        print(f"   Section: {result['section_used']}")
        
        # 6. List frames
        print("\n6. Listing all frames:")
        frames_result = await connector.send_command("list_frames")
        for frame in frames_result["data"]["frames"]:
            props = frame["properties"]
            start = props["startPoint"]
            end = props["endPoint"]
            print(f"   - {frame['name']}: {props['section']} (Length: {props['length']:.1f}m)")
            print(f"     From ({start['x']}, {start['y']}, {start['z']}) to ({end['x']}, {end['y']}, {end['z']})")
        
        print("\nDEMO COMPLETED SUCCESSFULLY!")
        
        # Show Claude examples
        print("\n" + "=" * 60)
        print("CLAUDE DESKTOP USAGE EXAMPLES")
        print("=" * 60)
        
        examples = [
            "Create points A1 through A5 at 5-meter spacing along the X-axis",
            "Create vertical columns from A points to B points using W14X90 sections", 
            "Show me all structural elements in the model",
            "Create a 4-bay building frame with standard steel sections"
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"\n{i}. \"{example}\"")
        
        print("\n" + "=" * 60)
        print("FEATURES DEMONSTRATED:")
        print("- Batch point creation from lists")
        print("- Pattern-based frame creation (A->B matching)")
        print("- Automatic coordinate extraction and frame naming")
        print("- Comprehensive error handling and reporting")
        print("- Natural language command support")
        
    except Exception as e:
        print(f"ERROR: Demo failed - {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting demo...")
    asyncio.run(main())