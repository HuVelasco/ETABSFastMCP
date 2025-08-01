using System;
using System.Collections.Generic;
using ETABSConnector.Models;

namespace ETABSConnector.Core
{
    /// <summary>
    /// Manages all frame-related operations in ETABS
    /// Provides comprehensive CRUD operations for structural frame elements
    /// </summary>
    public class FrameManager
    {
        private readonly ETABSConnectionManager _connectionManager;

        public FrameManager(ETABSConnectionManager connectionManager)
        {
            _connectionManager = connectionManager;
        }

        /// <summary>
        /// Create a new frame element in the ETABS model
        /// </summary>
        public CommandResponse CreateFrame(FrameRequest request)
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
                string frameName = request.Name ?? "";

                // Create frame by coordinates
                int ret = sapModel.FrameObj.AddByCoord(
                    request.StartPoint.X, request.StartPoint.Y, request.StartPoint.Z,
                    request.EndPoint.X, request.EndPoint.Y, request.EndPoint.Z,
                    ref frameName
                );

                if (ret != 0)
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = "Failed to create frame in ETABS"
                    };
                }

                // Set section if specified
                if (!string.IsNullOrEmpty(request.Section))
                {
                    sapModel.FrameObj.SetSection(frameName, request.Section);
                }

                // Set material if specified (this would require more complex material handling)
                if (!string.IsNullOrEmpty(request.Material))
                {
                    // Note: Material assignment typically requires section property modification
                    // For now, we'll store it as a property for future implementation
                }

                // Refresh view
                sapModel.View.RefreshView();

                return new CommandResponse
                {
                    Success = true,
                    Data = new
                    {
                        name = frameName,
                        startPoint = request.StartPoint,
                        endPoint = request.EndPoint,
                        section = request.Section,
                        material = request.Material,
                        length = CalculateLength(request.StartPoint, request.EndPoint),
                        message = "Frame created successfully"
                    }
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error creating frame: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Get information about a specific frame
        /// </summary>
        public CommandResponse GetFrame(string frameName)
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

                // Get frame points
                string pointI = "", pointJ = "";
                int ret = sapModel.FrameObj.GetPoints(frameName, ref pointI, ref pointJ);

                if (ret != 0)
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = $"Frame '{frameName}' not found"
                    };
                }

                // Get coordinates of end points
                double xi = 0, yi = 0, zi = 0, xj = 0, yj = 0, zj = 0;
                sapModel.PointObj.GetCoordCartesian(pointI, ref xi, ref yi, ref zi);
                sapModel.PointObj.GetCoordCartesian(pointJ, ref xj, ref yj, ref zj);

                // Get section
                string sectionName = "";
                string autoSelectListName = "";
                sapModel.FrameObj.GetSection(frameName, ref sectionName, ref autoSelectListName);

                var startPoint = new Point3D { X = xi, Y = yi, Z = zi };
                var endPoint = new Point3D { X = xj, Y = yj, Z = zj };

                var frameData = new ETABSObject
                {
                    Name = frameName,
                    Type = "Frame",
                    Properties = new Dictionary<string, object>
                    {
                        ["startPoint"] = startPoint,
                        ["endPoint"] = endPoint,
                        ["pointI"] = pointI,
                        ["pointJ"] = pointJ,
                        ["section"] = sectionName,
                        ["length"] = CalculateLength(startPoint, endPoint)
                    }
                };

                return new CommandResponse
                {
                    Success = true,
                    Data = frameData
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error getting frame: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// List all frames in the model
        /// </summary>
        public CommandResponse ListFrames()
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
                var frames = new List<ETABSObject>();

                int numberOfFrames = 0;
                string[]? frameNames = null;
                int ret = sapModel.FrameObj.GetNameList(ref numberOfFrames, ref frameNames);

                if (ret == 0 && frameNames != null)
                {
                    foreach (string frameName in frameNames)
                    {
                        // Get frame points
                        string pointI = "", pointJ = "";
                        sapModel.FrameObj.GetPoints(frameName, ref pointI, ref pointJ);

                        // Get coordinates
                        double xi = 0, yi = 0, zi = 0, xj = 0, yj = 0, zj = 0;
                        sapModel.PointObj.GetCoordCartesian(pointI, ref xi, ref yi, ref zi);
                        sapModel.PointObj.GetCoordCartesian(pointJ, ref xj, ref yj, ref zj);

                        // Get section
                        string sectionName = "";
                        string autoSelectListName = "";
                        sapModel.FrameObj.GetSection(frameName, ref sectionName, ref autoSelectListName);

                        var startPoint = new Point3D { X = xi, Y = yi, Z = zi };
                        var endPoint = new Point3D { X = xj, Y = yj, Z = zj };

                        frames.Add(new ETABSObject
                        {
                            Name = frameName,
                            Type = "Frame",
                            Properties = new Dictionary<string, object>
                            {
                                ["startPoint"] = startPoint,
                                ["endPoint"] = endPoint,
                                ["pointI"] = pointI,
                                ["pointJ"] = pointJ,
                                ["section"] = sectionName,
                                ["length"] = CalculateLength(startPoint, endPoint)
                            }
                        });
                    }
                }

                return new CommandResponse
                {
                    Success = true,
                    Data = new
                    {
                        count = frames.Count,
                        frames = frames
                    }
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error listing frames: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Modify an existing frame
        /// </summary>
        public CommandResponse ModifyFrame(string frameName, FrameRequest modifications)
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

                // Check if frame exists
                string pointI = "", pointJ = "";
                int ret = sapModel.FrameObj.GetPoints(frameName, ref pointI, ref pointJ);
                if (ret != 0)
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = $"Frame '{frameName}' not found"
                    };
                }

                var changes = new List<string>();

                // Update section if provided
                if (!string.IsNullOrEmpty(modifications.Section))
                {
                    ret = sapModel.FrameObj.SetSection(frameName, modifications.Section);
                    if (ret == 0)
                    {
                        changes.Add($"section changed to {modifications.Section}");
                    }
                }

                // Update coordinates if provided
                if (modifications.StartPoint != null && modifications.EndPoint != null)
                {
                    // For coordinate modification, we would need to update the end points
                    // This is more complex and might require recreation of the frame
                    changes.Add("coordinate modification requires frame recreation");
                }

                // Refresh view
                sapModel.View.RefreshView();

                return new CommandResponse
                {
                    Success = true,
                    Data = new
                    {
                        frameName = frameName,
                        changes = changes,
                        message = $"Frame '{frameName}' modified successfully"
                    }
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error modifying frame: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Delete a frame from the model
        /// </summary>
        public CommandResponse DeleteFrame(string frameName)
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

                int ret = sapModel.FrameObj.Delete(frameName);

                if (ret == 0)
                {
                    sapModel.View.RefreshView();
                    return new CommandResponse
                    {
                        Success = true,
                        Data = new { message = $"Frame '{frameName}' deleted successfully" }
                    };
                }
                else
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = $"Failed to delete frame '{frameName}'"
                    };
                }
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error deleting frame: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Calculate the length of a frame given start and end points
        /// </summary>
        private double CalculateLength(Point3D startPoint, Point3D endPoint)
        {
            double dx = endPoint.X - startPoint.X;
            double dy = endPoint.Y - startPoint.Y;
            double dz = endPoint.Z - startPoint.Z;
            return Math.Sqrt(dx * dx + dy * dy + dz * dz);
        }
    }
}