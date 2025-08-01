using System;
using System.IO;
using ETABSv1;
using ETABSConnector.Models;
using System.Runtime.InteropServices;

namespace ETABSConnector.Core
{
    /// <summary>
    /// Manages ETABS COM connection and basic operations
    /// Professional-grade connection manager with error handling and recovery
    /// </summary>
    public class ETABSConnectionManager : IDisposable
    {
        private cOAPI? _sapObject;
        private cSapModel? _sapModel;
        private bool _isConnected;

        public bool IsConnected => _isConnected && _sapModel != null;
        public cSapModel SapModel => _sapModel ?? throw new InvalidOperationException("Not connected to ETABS");

        /// <summary>
        /// Connect to ETABS application
        /// </summary>
        public CommandResponse Connect(bool attachToExisting = true)
        {

            try
            {
                Console.WriteLine("Attempting to connect to ETABS...");

                if (_isConnected)
                {
                    return new CommandResponse
                    {
                        Success = true,
                        Data = new { message = "Already connected to ETABS", connected = true }
                    };
                }

                    if (attachToExisting)
                {
                    return AttachToExistingInstance();
                }
                else
                {
                    return CreateNewInstance();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ERROR: Failed to connect to ETABS: {ex.Message}");
                return new CommandResponse
                {
                    Success = false,
                    Error = $"ERROR: Failed to connect to ETABS: {ex.Message}"
                };
            }

            
             
        }

        /// <summary>
        /// Attempts to attach to an existing ETABS instance
        /// </summary>
        private CommandResponse AttachToExistingInstance()
        {
            try
            {
                Console.WriteLine("Trying to attach to existing ETABS instance...");

                // Get the active ETABS object
                _sapObject = (cOAPI)Marshal.GetActiveObject("CSI.ETABS.API.ETABSObject");

                Console.WriteLine("SUCCESS: Attached to existing ETABS instance");

                _isConnected = true;
                return new CommandResponse
                {
                    Success = true,
                    Data = new
                    {
                        message = "Connected to existing ETABS instance",
                        method = "attach",
                        connected = true
                    }
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"No existing instance found: {ex.Message}");
                return new CommandResponse
                {
                    Success = false,
                    Error = "Failed to connect to an existing instance of ETABS"
                };
            }
        }

        /// <summary>
        /// Creates a new ETABS instance
        /// </summary>
        private CommandResponse CreateNewInstance()
        {
            try
            {
                Console.WriteLine("Creating new ETABS instance...");

                // Create API helper object
                cHelper myHelper = new Helper();

                // Create ETABS object using ProgID (automatically finds latest installation)
                _sapObject = myHelper.CreateObjectProgID("CSI.ETABS.API.ETABSObject");

                Console.WriteLine("SUCCESS: Created ETABS API object");

                // Start ETABS application
                int ret = _sapObject.ApplicationStart();
                if (ret != 0)
                {
                    Console.WriteLine($"WARNING: ApplicationStart returned {ret}");
                }
                else
                {
                    Console.WriteLine("SUCCESS: ETABS application started");
                }

                _isConnected = true;
                return new CommandResponse
                {
                    Success = true,
                    Data = new
                    {
                        message = "Connected to ETABS (new instance)",
                        method = "new",
                        connected = true
                    }
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Failed to create new instance: {ex.Message}");
                return new CommandResponse
                {
                    Success = false,
                    Error = "Failed to initialize New ETABS connection"
                };
            }
        }

        /// <summary>
        /// Create new blank ETABS model
        /// </summary>
        public CommandResponse CreateBlankModel()
        {
            if (!IsConnected)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = "Not connected to ETABS"
                };
            }

            try
            {
                int ret = _sapModel!.InitializeNewModel();
                if (ret != 0)
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = "Failed to initialize new model"
                    };
                }

                ret = _sapModel.File.NewBlank();
                if (ret != 0)
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = "Failed to create blank model"
                    };
                }

                // Set basic model properties
                _sapModel.SetPresentUnits(eUnits.kN_m_C);

                return new CommandResponse
                {
                    Success = true,
                    Data = new { 
                        message = "Blank model created successfully",
                        units = "kN_m_C"
                    }
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error creating blank model: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Get connection status and model information
        /// </summary>
        public CommandResponse GetStatus()
        {
            try
            {
                var status = new ConnectionStatus
                {
                    Connected = IsConnected
                };

                if (IsConnected && _sapModel != null)
                {
                    // Get model information
                    string modelPath = "";
                    modelPath = _sapModel.GetModelFilename(false);
                    status.ModelPath = modelPath;



                    // Get ETABS version (simplified)
                    status.Version = "ETABS v18+";
                    status.LastCommand = DateTime.Now;
                }

                return new CommandResponse
                {
                    Success = true,
                    Data = status
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error getting status: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Save current model
        /// </summary>
        public CommandResponse SaveModel(string? filePath = null)
        {
            if (!IsConnected)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = "Not connected to ETABS"
                };
            }

            try
            {
                int ret;
                if (!string.IsNullOrEmpty(filePath))
                {
                    ret = _sapModel!.File.Save(filePath);
                }
                else
                {
                    ret = _sapModel!.File.Save();
                }

                if (ret == 0)
                {
                    return new CommandResponse
                    {
                        Success = true,
                        Data = new { message = "Model saved successfully", path = filePath }
                    };
                }
                else
                {
                    return new CommandResponse
                    {
                        Success = false,
                        Error = "Failed to save model"
                    };
                }
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error saving model: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Disconnect from ETABS
        /// </summary>
        public CommandResponse Disconnect(bool exitApplication = false)
        {
            try
            {
                if (_isConnected && exitApplication && _sapObject != null)
                {
                    _sapObject.ApplicationExit(false);
                }

                _sapModel = null;
                _sapObject = null;
                _isConnected = false;

                return new CommandResponse
                {
                    Success = true,
                    Data = new { message = "Disconnected from ETABS", exitedApplication = exitApplication }
                };
            }
            catch (Exception ex)
            {
                _isConnected = false;
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error during disconnect: {ex.Message}"
                };
            }
        }

        public void Dispose()
        {
            Disconnect(false);
        }
    }
}