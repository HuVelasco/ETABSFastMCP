using System;
using System.IO;
using System.Collections.Generic;
using Newtonsoft.Json;
using ETABSConnector.Models;

namespace ETABSConnector.Core
{
    // Helper Class
    public static class DictionaryExtensions
    {
        public static TValue GetValueOrDefault<TKey, TValue>(this Dictionary<TKey, TValue> dictionary, TKey key, TValue defaultValue = default)
        {
            return dictionary.TryGetValue(key, out var value) ? value : defaultValue;
        }
    }


    /// <summary>
    /// Main command processor for stdio communication
    /// Routes commands to appropriate managers and handles serialization
    /// </summary>
    public class CommandProcessor : IDisposable
    {
        private readonly ETABSConnectionManager _connectionManager;
        private readonly PointManager _pointManager;
        private readonly FrameManager _frameManager;
        private readonly TextReader _input;
        private readonly TextWriter _output;
        private readonly TextWriter _error;

        public CommandProcessor(TextReader? input = null, TextWriter? output = null, TextWriter? error = null)
        {
            _input = input ?? Console.In;
            _output = output ?? Console.Out;
            _error = error ?? Console.Error;

            _connectionManager = new ETABSConnectionManager();
            _pointManager = new PointManager(_connectionManager);
            _frameManager = new FrameManager(_connectionManager);
        }

        /// <summary>
        /// Start processing commands from stdin
        /// </summary>
        public void StartProcessing()
        {
            _error.WriteLine("ETABS Connector started. Waiting for commands...");

            // Test some fuctions as the commands giev error:
            _connectionManager.Connect(true);
            _connectionManager.Connect(false);
            _connectionManager.GetStatus();
            _connectionManager.CreateBlankModel();


            try
            {
                string? line;
                while ((line = _input.ReadLine()) != null)
                {
                    if (string.IsNullOrWhiteSpace(line))
                        continue;

                    try
                    {
                        var command = JsonConvert.DeserializeObject<Command>(line);
                        if (command != null)
                        {
                            var response = ProcessCommand(command);
                            response.Id = command.Id;
                            
                            string responseJson = JsonConvert.SerializeObject(response);
                            _output.WriteLine(responseJson);
                            _output.Flush();
                        }
                    }
                    catch (JsonException ex)
                    {
                        var errorResponse = new CommandResponse
                        {
                            Success = false,
                            Error = $"Invalid JSON command: {ex.Message}"
                        };
                        
                        string responseJson = JsonConvert.SerializeObject(errorResponse);
                        _output.WriteLine(responseJson);
                        _output.Flush();
                    }
                    catch (Exception ex)
                    {
                        _error.WriteLine($"Unexpected error: {ex.Message}");
                        var errorResponse = new CommandResponse
                        {
                            Success = false,
                            Error = $"Unexpected error: {ex.Message}"
                        };
                        
                        string responseJson = JsonConvert.SerializeObject(errorResponse);
                        _output.WriteLine(responseJson);
                        _output.Flush();
                    }
                }
            }
            catch (Exception ex)
            {
                _error.WriteLine($"Fatal error in command processing: {ex.Message}");
            }
        }

        /// <summary>
        /// Process a single command and return response
        /// </summary>
        private CommandResponse ProcessCommand(Command command)
        {
            try
            {
                return command.Action.ToLower() switch
                {
                    // Connection commands
                    "connect" => _connectionManager.Connect(
                        command.Parameters.GetValueOrDefault("attachToExisting", true) is bool attach ? attach : true),
                    "disconnect" => _connectionManager.Disconnect(
                        command.Parameters.GetValueOrDefault("exitApplication", false) is bool exit ? exit : false),
                    "status" => _connectionManager.GetStatus(),
                    "create_blank_model" => _connectionManager.CreateBlankModel(),
                    "save_model" => _connectionManager.SaveModel(
                        command.Parameters.GetValueOrDefault("filePath", null) as string),

                    // Point commands
                    "create_point" => ProcessPointCommand("create", command.Parameters),
                    "get_point" => ProcessPointCommand("get", command.Parameters),
                    "list_points" => _pointManager.ListPoints(),
                    "modify_point" => ProcessPointCommand("modify", command.Parameters),
                    "delete_point" => ProcessPointCommand("delete", command.Parameters),

                    // Frame commands
                    "create_frame" => ProcessFrameCommand("create", command.Parameters),
                    "get_frame" => ProcessFrameCommand("get", command.Parameters),
                    "list_frames" => _frameManager.ListFrames(),
                    "modify_frame" => ProcessFrameCommand("modify", command.Parameters),
                    "delete_frame" => ProcessFrameCommand("delete", command.Parameters),

                    // Health check
                    "ping" => new CommandResponse { Success = true, Data = "pong" },

                    _ => new CommandResponse
                    {
                        Success = false,
                        Error = $"Unknown command: {command.Action}"
                    }
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error processing command '{command.Action}': {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Process point-specific commands
        /// </summary>
        private CommandResponse ProcessPointCommand(string operation, Dictionary<string, object> parameters)
        {
            try
            {
                return operation switch
                {
                    "create" => _pointManager.CreatePoint(ParsePointRequest(parameters)),
                    "get" => _pointManager.GetPoint(parameters.GetValueOrDefault("name", "") as string ?? ""),
                    "modify" => _pointManager.ModifyPoint(
                        parameters.GetValueOrDefault("name", "") as string ?? "",
                        ParsePointRequest(parameters)),
                    "delete" => _pointManager.DeletePoint(parameters.GetValueOrDefault("name", "") as string ?? ""),
                    _ => new CommandResponse { Success = false, Error = $"Unknown point operation: {operation}" }
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error in point operation '{operation}': {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Process frame-specific commands
        /// </summary>
        private CommandResponse ProcessFrameCommand(string operation, Dictionary<string, object> parameters)
        {
            try
            {
                return operation switch
                {
                    "create" => _frameManager.CreateFrame(ParseFrameRequest(parameters)),
                    "get" => _frameManager.GetFrame(parameters.GetValueOrDefault("name", "") as string ?? ""),
                    "modify" => _frameManager.ModifyFrame(
                        parameters.GetValueOrDefault("name", "") as string ?? "",
                        ParseFrameRequest(parameters)),
                    "delete" => _frameManager.DeleteFrame(parameters.GetValueOrDefault("name", "") as string ?? ""),
                    _ => new CommandResponse { Success = false, Error = $"Unknown frame operation: {operation}" }
                };
            }
            catch (Exception ex)
            {
                return new CommandResponse
                {
                    Success = false,
                    Error = $"Error in frame operation '{operation}': {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Parse parameters into PointRequest object
        /// </summary>
        private PointRequest ParsePointRequest(Dictionary<string, object> parameters)
        {
            var request = new PointRequest();

            if (parameters.TryGetValue("name", out var nameObj))
                request.Name = nameObj as string;

            if (parameters.TryGetValue("coordinates", out var coordObj))
            {
                if (coordObj is Newtonsoft.Json.Linq.JObject coordJson)
                {
                    request.Coordinates = coordJson.ToObject<Point3D>() ?? new Point3D();
                }
            }

            if (parameters.TryGetValue("restraints", out var restraintObj))
            {
                if (restraintObj is Newtonsoft.Json.Linq.JObject restraintJson)
                {
                    request.Restraints = restraintJson.ToObject<Dictionary<string, bool>>();
                }
            }

            if (parameters.TryGetValue("properties", out var propObj))
            {
                if (propObj is Newtonsoft.Json.Linq.JObject propJson)
                {
                    request.Properties = propJson.ToObject<Dictionary<string, object>>();
                }
            }

            return request;
        }

        /// <summary>
        /// Parse parameters into FrameRequest object
        /// </summary>
        private FrameRequest ParseFrameRequest(Dictionary<string, object> parameters)
        {
            var request = new FrameRequest();

            if (parameters.TryGetValue("name", out var nameObj))
                request.Name = nameObj as string;

            if (parameters.TryGetValue("startPoint", out var startObj))
            {
                if (startObj is Newtonsoft.Json.Linq.JObject startJson)
                {
                    request.StartPoint = startJson.ToObject<Point3D>() ?? new Point3D();
                }
            }

            if (parameters.TryGetValue("endPoint", out var endObj))
            {
                if (endObj is Newtonsoft.Json.Linq.JObject endJson)
                {
                    request.EndPoint = endJson.ToObject<Point3D>() ?? new Point3D();
                }
            }

            if (parameters.TryGetValue("section", out var sectionObj))
                request.Section = sectionObj as string;

            if (parameters.TryGetValue("material", out var materialObj))
                request.Material = materialObj as string;

            if (parameters.TryGetValue("properties", out var propObj))
            {
                if (propObj is Newtonsoft.Json.Linq.JObject propJson)
                {
                    request.Properties = propJson.ToObject<Dictionary<string, object>>();
                }
            }

            return request;
        }

        public void Dispose()
        {
            _connectionManager?.Dispose();
        }
    }
}