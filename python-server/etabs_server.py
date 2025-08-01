#!/usr/bin/env python3
"""
ETABS FastMCP Server
Professional-grade MCP server for ETABS structural analysis software
Uses FastMCP patterns for seamless Claude Desktop integration
"""

import asyncio
import json
import logging
import subprocess
import uuid
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("ETABS Structural Analysis")

class Point3D(BaseModel):
    """3D point coordinates"""
    x: float = Field(description="X coordinate")
    y: float = Field(description="Y coordinate") 
    z: float = Field(description="Z coordinate")

class PointRequest(BaseModel):
    """Point creation/modification request"""
    name: Optional[str] = Field(None, description="Point name (auto-generated if not provided)")
    coordinates: Point3D = Field(description="Point coordinates")
    restraints: Optional[Dict[str, bool]] = Field(None, description="Point restraints (UX, UY, UZ, RX, RY, RZ)")
    properties: Optional[Dict[str, Any]] = Field(None, description="Additional point properties")

class FrameRequest(BaseModel):
    """Frame creation/modification request"""
    name: Optional[str] = Field(None, description="Frame name (auto-generated if not provided)")
    start_point: Point3D = Field(description="Frame start point coordinates")
    end_point: Point3D = Field(description="Frame end point coordinates")
    section: Optional[str] = Field(None, description="Frame section (e.g., W14X90)")
    material: Optional[str] = Field(None, description="Frame material (e.g., A992)")
    properties: Optional[Dict[str, Any]] = Field(None, description="Additional frame properties")

class ETABSConnector:
    """Manages communication with C# ETABS connector via stdio"""
    
    def __init__(self, connector_path: str):
        self.connector_path = Path(connector_path)
        self.process: Optional[subprocess.Popen] = None
        
    async def start(self):
        """Start the C# connector process"""
        try:
            self.process = subprocess.Popen(
                [str(self.connector_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            logger.info(f"Started ETABS connector process: PID {self.process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start ETABS connector: {e}")
            return False
    
    async def send_command(self, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send command to C# connector and return response"""
        if not self.process or self.process.poll() is not None:
            raise RuntimeError("ETABS connector is not running")
        
        command = {
            "id": str(uuid.uuid4()),
            "action": action,
            "parameters": parameters or {}
        }
        
        try:
            # Send command
            command_json = json.dumps(command) + "\n"
            self.process.stdin.write(command_json)
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline().strip()
            if not response_line:
                raise RuntimeError("No response from ETABS connector")
            
            response = json.loads(response_line)
            return response
            
        except Exception as e:
            logger.error(f"Communication error with ETABS connector: {e}")
            raise RuntimeError(f"Failed to communicate with ETABS: {e}")
    
    async def stop(self):
        """Stop the C# connector process"""
        if self.process:
            try:
                await self.send_command("disconnect", {"exitApplication": False})
            except:
                pass  # Process might already be dead
            
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            
            self.process = None
            logger.info("ETABS connector process stopped")

# Global connector instance
connector = ETABSConnector(
    str(Path(__file__).parent.parent / "csharp-connector" / "bin" / "Debug" / "ETABSConnector.exe")
)

@mcp.tool()
async def connect_to_etabs(attach_to_existing: bool = True) -> Dict[str, Any]:
    """
    Connect to ETABS application
    
    Args:
        attach_to_existing: Whether to attach to existing ETABS instance or start new one
        
    Returns:
        Connection status and information
    """
    try:
        # Start connector if not running
        if not connector.process or connector.process.poll() is not None:
            success = await connector.start()
            if not success:
                return {"success": False, "error": "Failed to start ETABS connector"}
        
        # Send connect command
        response = await connector.send_command("connect", {
            "attachToExisting": attach_to_existing
        })
        
        return response
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def create_blank_model() -> Dict[str, Any]:
    """
    Create a new blank ETABS model
    
    Returns:
        Success status and model information
    """
    try:
        response = await connector.send_command("create_blank_model")
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_connection_status() -> Dict[str, Any]:
    """
    Get current ETABS connection status and model information
    
    Returns:
        Connection status, model path, version info
    """
    try:
        response = await connector.send_command("status")
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def create_point(
    x: float,
    y: float, 
    z: float,
    name: Optional[str] = None,
    restraints: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    """
    Create a new point in the ETABS model
    
    Args:
        x: X coordinate
        y: Y coordinate  
        z: Z coordinate
        name: Point name (auto-generated if not provided)
        restraints: Point restraints dict with keys UX, UY, UZ, RX, RY, RZ
        
    Returns:
        Created point information
    """
    try:
        parameters = {
            "name": name,
            "coordinates": {"x": x, "y": y, "z": z}
        }
        
        if restraints:
            parameters["restraints"] = restraints
            
        response = await connector.send_command("create_point", parameters)
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def create_points_batch(
    points: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create multiple points in the ETABS model from a list
    
    Args:
        points: List of point definitions, each containing:
            - name: Point name
            - x, y, z: Coordinates
            - restraints: Optional restraints dict
            
    Example:
        points = [
            {"name": "A1", "x": 0, "y": 0, "z": 0, "restraints": {"UZ": True}},
            {"name": "A2", "x": 10, "y": 0, "z": 0},
            {"name": "B1", "x": 0, "y": 10, "z": 0},
            {"name": "B2", "x": 10, "y": 10, "z": 0}
        ]
        
    Returns:
        Results of all point creation operations
    """
    try:
        results = []
        successful_points = []
        failed_points = []
        
        for point_def in points:
            try:
                # Extract point data
                name = point_def.get("name")
                x = point_def.get("x", 0.0)
                y = point_def.get("y", 0.0)
                z = point_def.get("z", 0.0)
                restraints = point_def.get("restraints")
                
                # Create the point
                result = await create_point(x, y, z, name, restraints)
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
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def create_frames_by_pattern(
    start_pattern: str = "A",
    end_pattern: str = "B",
    section: Optional[str] = None,
    material: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create frame elements automatically by matching point name patterns
    
    Args:
        start_pattern: Pattern for start points (e.g., "A" matches A1, A2, etc.)
        end_pattern: Pattern for end points (e.g., "B" matches B1, B2, etc.)
        section: Frame section (e.g., W14X90)
        material: Frame material (e.g., A992)
        
    Example:
        If you have points A1, A2, B1, B2, this will create:
        - Frame A1-B1: from A1 to B1
        - Frame A2-B2: from A2 to B2
        
    Returns:
        Results of all frame creation operations
    """
    try:
        # First get all points in the model
        points_result = await list_points()
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
                # Extract the suffix (e.g., "1" from "A1")
                suffix = point_name[len(start_pattern):]
                start_points[suffix] = point
            elif point_name.startswith(end_pattern):
                suffix = point_name[len(end_pattern):]
                end_points[suffix] = point
        
        # Find matching pairs
        successful_frames = []
        failed_frames = []
        
        for suffix in start_points:
            if suffix in end_points:
                start_point = start_points[suffix]
                end_point = end_points[suffix]
                
                # Get coordinates
                start_coords = start_point["properties"]["coordinates"]
                end_coords = end_point["properties"]["coordinates"]
                
                # Create frame name
                frame_name = f"{start_point['name']}-{end_point['name']}"
                
                try:
                    # Create the frame
                    result = await create_frame(
                        start_x=start_coords["x"],
                        start_y=start_coords["y"],
                        start_z=start_coords["z"],
                        end_x=end_coords["x"],
                        end_y=end_coords["y"],
                        end_z=end_coords["z"],
                        name=frame_name,
                        section=section,
                        material=material
                    )
                    
                    if result.get("success", False):
                        successful_frames.append(frame_name)
                    else:
                        failed_frames.append({"name": frame_name, "error": result.get("error", "Unknown error")})
                        
                except Exception as e:
                    failed_frames.append({"name": frame_name, "error": str(e)})
            else:
                # No matching end point found
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
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_point(name: str) -> Dict[str, Any]:
    """
    Get information about a specific point
    
    Args:
        name: Point name
        
    Returns:
        Point information including coordinates and restraints
    """
    try:
        response = await connector.send_command("get_point", {"name": name})
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def list_points() -> Dict[str, Any]:
    """
    List all points in the ETABS model
    
    Returns:
        List of all points with their properties
    """
    try:
        response = await connector.send_command("list_points")
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def modify_point(
    name: str,
    x: Optional[float] = None,
    y: Optional[float] = None,
    z: Optional[float] = None,
    restraints: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    """
    Modify an existing point's properties
    
    Args:
        name: Point name to modify
        x: New X coordinate (optional)
        y: New Y coordinate (optional)
        z: New Z coordinate (optional)
        restraints: New restraints dict (optional)
        
    Returns:
        Modification results
    """
    try:
        parameters = {"name": name}
        
        if any(coord is not None for coord in [x, y, z]):
            coordinates = {}
            if x is not None: coordinates["x"] = x
            if y is not None: coordinates["y"] = y  
            if z is not None: coordinates["z"] = z
            parameters["coordinates"] = coordinates
            
        if restraints:
            parameters["restraints"] = restraints
            
        response = await connector.send_command("modify_point", parameters)
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def delete_point(name: str) -> Dict[str, Any]:
    """
    Delete a point from the ETABS model
    
    Args:
        name: Point name to delete
        
    Returns:
        Deletion results
    """
    try:
        response = await connector.send_command("delete_point", {"name": name})
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def create_frame(
    start_x: float,
    start_y: float,
    start_z: float,
    end_x: float,
    end_y: float,
    end_z: float,
    name: Optional[str] = None,
    section: Optional[str] = None,
    material: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new frame element in the ETABS model
    
    Args:
        start_x: Start point X coordinate
        start_y: Start point Y coordinate
        start_z: Start point Z coordinate
        end_x: End point X coordinate
        end_y: End point Y coordinate
        end_z: End point Z coordinate
        name: Frame name (auto-generated if not provided)
        section: Frame section (e.g., W14X90)
        material: Frame material (e.g., A992)
        
    Returns:
        Created frame information
    """
    try:
        parameters = {
            "name": name,
            "startPoint": {"x": start_x, "y": start_y, "z": start_z},
            "endPoint": {"x": end_x, "y": end_y, "z": end_z}
        }
        
        if section:
            parameters["section"] = section
        if material:
            parameters["material"] = material
            
        response = await connector.send_command("create_frame", parameters)
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_frame(name: str) -> Dict[str, Any]:
    """
    Get information about a specific frame
    
    Args:
        name: Frame name
        
    Returns:
        Frame information including coordinates, section, and properties
    """
    try:
        response = await connector.send_command("get_frame", {"name": name})
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def list_frames() -> Dict[str, Any]:
    """
    List all frame elements in the ETABS model
    
    Returns:
        List of all frames with their properties
    """
    try:
        response = await connector.send_command("list_frames")
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def modify_frame(
    name: str,
    section: Optional[str] = None,
    material: Optional[str] = None
) -> Dict[str, Any]:
    """
    Modify an existing frame's properties
    
    Args:
        name: Frame name to modify
        section: New frame section (optional)
        material: New frame material (optional)
        
    Returns:
        Modification results
    """
    try:
        parameters = {"name": name}
        
        if section:
            parameters["section"] = section
        if material:
            parameters["material"] = material
            
        response = await connector.send_command("modify_frame", parameters)
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def delete_frame(name: str) -> Dict[str, Any]:
    """
    Delete a frame from the ETABS model
    
    Args:
        name: Frame name to delete
        
    Returns:
        Deletion results
    """
    try:
        response = await connector.send_command("delete_frame", {"name": name})
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def save_model(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Save the current ETABS model
    
    Args:
        file_path: Path to save the model (optional, uses current path if not provided)
        
    Returns:
        Save operation results
    """
    try:
        parameters = {}
        if file_path:
            parameters["filePath"] = file_path
            
        response = await connector.send_command("save_model", parameters)
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def disconnect_from_etabs(exit_application: bool = False) -> Dict[str, Any]:
    """
    Disconnect from ETABS application
    
    Args:
        exit_application: Whether to exit ETABS application completely
        
    Returns:
        Disconnection status
    """
    try:
        response = await connector.send_command("disconnect", {
            "exitApplication": exit_application
        })
        
        # Stop connector process
        await connector.stop()
        
        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

# Server lifecycle management
@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """
    Check the health of the ETABS MCP server and connector
    
    Returns:
        Health status of all components
    """
    try:
        # Check if connector process is running
        connector_running = connector.process is not None and connector.process.poll() is None
        
        if connector_running:
            # Try to ping the connector
            try:
                response = await connector.send_command("ping")
                connector_responsive = response.get("success", False)
            except:
                connector_responsive = False
        else:
            connector_responsive = False
        
        return {
            "success": True,
            "server": "running",
            "connector_process": "running" if connector_running else "stopped",
            "connector_responsive": connector_responsive,
            "timestamp": "2025-01-01T00:00:00Z"  # Would use actual timestamp
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # This enables the server to be run directly for testing
    import mcp.server.stdio
    
    async def main():
        # Run the MCP server
        async with mcp.stdio_server() as (read_stream, write_stream):
            await mcp.run(
                read_stream, write_stream,
                mcp.create_initialization_options()
            )
    
    asyncio.run(main())