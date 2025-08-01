using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace ETABSConnector.Models
{
    /// <summary>
    /// Base command structure for stdio communication
    /// </summary>
    public class Command
    {
        [JsonProperty("id")]
        public string Id { get; set; } = "";

        [JsonProperty("action")]
        public string Action { get; set; } = "";

        [JsonProperty("parameters")]
        public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Response structure for all commands
    /// </summary>
    public class CommandResponse
    {
        [JsonProperty("id")]
        public string Id { get; set; } = "";

        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("data")]
        public object? Data { get; set; }

        [JsonProperty("error")]
        public string? Error { get; set; }

        [JsonProperty("timestamp")]
        public DateTime Timestamp { get; set; } = DateTime.Now;
    }

    /// <summary>
    /// Point data structure
    /// </summary>
    public class Point3D
    {
        [JsonProperty("x")]
        public double X { get; set; }

        [JsonProperty("y")]
        public double Y { get; set; }

        [JsonProperty("z")]
        public double Z { get; set; }
    }

    /// <summary>
    /// Point creation/modification request
    /// </summary>
    public class PointRequest
    {
        [JsonProperty("name")]
        public string? Name { get; set; }

        [JsonProperty("coordinates")]
        public Point3D Coordinates { get; set; } = new Point3D();

        [JsonProperty("restraints")]
        public Dictionary<string, bool>? Restraints { get; set; }

        [JsonProperty("properties")]
        public Dictionary<string, object>? Properties { get; set; }
    }

    /// <summary>
    /// Frame creation/modification request
    /// </summary>
    public class FrameRequest
    {
        [JsonProperty("name")]
        public string? Name { get; set; }

        [JsonProperty("startPoint")]
        public Point3D StartPoint { get; set; } = new Point3D();

        [JsonProperty("endPoint")]
        public Point3D EndPoint { get; set; } = new Point3D();

        [JsonProperty("section")]
        public string? Section { get; set; }

        [JsonProperty("material")]
        public string? Material { get; set; }

        [JsonProperty("properties")]
        public Dictionary<string, object>? Properties { get; set; }
    }

    /// <summary>
    /// ETABS object data returned from queries
    /// </summary>
    public class ETABSObject
    {
        [JsonProperty("name")]
        public string Name { get; set; } = "";

        [JsonProperty("type")]
        public string Type { get; set; } = "";

        [JsonProperty("properties")]
        public Dictionary<string, object> Properties { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Connection status information
    /// </summary>
    public class ConnectionStatus
    {
        [JsonProperty("connected")]
        public bool Connected { get; set; }

        [JsonProperty("version")]
        public string? Version { get; set; }

        [JsonProperty("modelPath")]
        public string? ModelPath { get; set; }

        [JsonProperty("modelName")]
        public string? ModelName { get; set; }

        [JsonProperty("lastCommand")]
        public DateTime? LastCommand { get; set; }
    }
}