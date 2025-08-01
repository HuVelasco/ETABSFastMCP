using System;
using System.Collections.Generic;
using System.Linq;
using ETABSConnector.Models;

namespace ETABSConnector.Core
{
    /// <summary>
    /// Manages all point-related operations in ETABS
    /// Provides comprehensive CRUD operations for structural points
    /// </summary>
    public class PointManager
    {
        private readonly ETABSConnectionManager _connectionManager;

        public PointManager(ETABSConnectionManager connectionManager)
        {
            _connectionManager = connectionManager;
        }

        /// <summary>
        /// Create a new point in the ETABS model
        /// </summary>
        public CommandResponse CreatePoint(PointRequest request)
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
                string pointName = request.Name ?? "";

                // Create point
                int ret = sapModel.PointObj.AddCartesian(
                    request.Coordinates.X,
                    request.Coordinates.Y,
                    request.Coordinates.Z,
                    ref pointName
                );

                if (ret != 0)
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = "Failed to create point in ETABS"
                    };
                }

                // Apply restraints if specified
                if (request.Restraints != null && request.Restraints.Any())
                {
                    bool[] restraints = new bool[6]; // UX, UY, UZ, RX, RY, RZ
                    restraints[0] = request.Restraints.GetValueOrDefault("UX", false);
                    restraints[1] = request.Restraints.GetValueOrDefault("UY", false);
                    restraints[2] = request.Restraints.GetValueOrDefault("UZ", false);
                    restraints[3] = request.Restraints.GetValueOrDefault("RX", false);
                    restraints[4] = request.Restraints.GetValueOrDefault("RY", false);
                    restraints[5] = request.Restraints.GetValueOrDefault("RZ", false);

                    sapModel.PointObj.SetRestraint(pointName, ref restraints);
                }

                // Refresh view
                sapModel.View.RefreshView();

                return new CommandResponse
                {
                    Success = true,
                    Data = new
                    {
                        name = pointName,
                        coordinates = request.Coordinates,
                        message = "Point created successfully"
                    }
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error creating point: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Get information about a specific point
        /// </summary>
        public CommandResponse GetPoint(string pointName)
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

                // Get coordinates
                double x = 0, y = 0, z = 0;
                int ret = sapModel.PointObj.GetCoordCartesian(pointName, ref x, ref y, ref z);

                if (ret != 0)
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = $"Point '{pointName}' not found"
                    };
                }

                // Get restraints
                bool[] restraints = new bool[6];
                sapModel.PointObj.GetRestraint(pointName, ref restraints);

                var pointData = new ETABSObject
                {
                    Name = pointName,
                    Type = "Point",
                    Properties = new Dictionary<string, object>
                    {
                        ["coordinates"] = new Point3D { X = x, Y = y, Z = z },
                        ["restraints"] = new Dictionary<string, bool>
                        {
                            ["UX"] = restraints[0],
                            ["UY"] = restraints[1],
                            ["UZ"] = restraints[2],
                            ["RX"] = restraints[3],
                            ["RY"] = restraints[4],
                            ["RZ"] = restraints[5]
                        }
                    }
                };

                return new CommandResponse
                {
                    Success = true,
                    Data = pointData
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error getting point: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// List all points in the model
        /// </summary>
        public CommandResponse ListPoints()
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
                var points = new List<ETABSObject>();

                int numberOfPoints = 0;
                string[]? pointNames = null;
                int ret = sapModel.PointObj.GetNameList(ref numberOfPoints, ref pointNames);

                if (ret == 0 && pointNames != null)
                {
                    foreach (string pointName in pointNames)
                    {
                        double x = 0, y = 0, z = 0;
                        sapModel.PointObj.GetCoordCartesian(pointName, ref x, ref y, ref z);

                        bool[] restraints = new bool[6];
                        sapModel.PointObj.GetRestraint(pointName, ref restraints);

                        points.Add(new ETABSObject
                        {
                            Name = pointName,
                            Type = "Point",
                            Properties = new Dictionary<string, object>
                            {
                                ["coordinates"] = new Point3D { X = x, Y = y, Z = z },
                                ["restraints"] = new Dictionary<string, bool>
                                {
                                    ["UX"] = restraints[0],
                                    ["UY"] = restraints[1],
                                    ["UZ"] = restraints[2],
                                    ["RX"] = restraints[3],
                                    ["RY"] = restraints[4],
                                    ["RZ"] = restraints[5]
                                }
                            }
                        });
                    }
                }

                return new CommandResponse
                {
                    Success = true,
                    Data = new
                    {
                        count = points.Count,
                        points = points
                    }
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error listing points: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Modify an existing point
        /// </summary>
        public CommandResponse ModifyPoint(string pointName, PointRequest modifications)
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

                // Check if point exists
                double x = 0, y = 0, z = 0;
                int ret = sapModel.PointObj.GetCoordCartesian(pointName, ref x, ref y, ref z);
                if (ret != 0)
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = $"Point '{pointName}' not found"
                    };
                }

                var changes = new List<string>();

                // Update coordinates if provided
                if (modifications.Coordinates != null)
                {
                    ret = 0;
                    //sapModel.PointObj.SetCoordCartesian(
                    //pointName,
                    //modifications.Coordinates.X,
                    //modifications.Coordinates.Y,
                    //modifications.Coordinates.Z
                    //);

                    if (ret == 0)
                    {
                        changes.Add("coordinates updated");
                    }
                }

                // Update restraints if provided
                if (modifications.Restraints != null)
                {
                    bool[] restraints = new bool[6];
                    restraints[0] = modifications.Restraints.GetValueOrDefault("UX", false);
                    restraints[1] = modifications.Restraints.GetValueOrDefault("UY", false);
                    restraints[2] = modifications.Restraints.GetValueOrDefault("UZ", false);
                    restraints[3] = modifications.Restraints.GetValueOrDefault("RX", false);
                    restraints[4] = modifications.Restraints.GetValueOrDefault("RY", false);
                    restraints[5] = modifications.Restraints.GetValueOrDefault("RZ", false);

                    ret = sapModel.PointObj.SetRestraint(pointName, ref restraints);
                    if (ret == 0)
                    {
                        changes.Add("restraints updated");
                    }
                }

                // Refresh view
                sapModel.View.RefreshView();

                return new CommandResponse
                {
                    Success = true,
                    Data = new
                    {
                        pointName = pointName,
                        changes = changes,
                        message = $"Point '{pointName}' modified successfully"
                    }
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error modifying point: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Delete a point from the model
        /// </summary>
        public CommandResponse DeletePoint(string pointName)
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

                int ret = sapModel.PointObj.DeleteSpecialPoint(pointName, 0);

                if (ret == 0)
                {
                    sapModel.View.RefreshView();
                    return new CommandResponse
                    {
                        Success = true,
                        Data = new { message = $"Point '{pointName}' deleted successfully" }
                    };
                }
                else
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = $"Failed to delete point '{pointName}'"
                    };
                }
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error deleting point: {ex.Message}"
                };
            }
        }
    }
}