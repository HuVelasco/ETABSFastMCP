using System;
using ETABSConnector.Core;

namespace ETABSConnector
{
    /// <summary>
    /// ETABS C# Connector - Stdio-based ETABS API connector
    /// Communicates with Python FastMCP server via stdin/stdout
    /// Professional-grade production-ready connector
    /// </summary>
    class Program
    {
        static void Main(string[] args)
        {
            // Set up error logging
            Console.Error.WriteLine($"ETABS Connector v1.0 starting at {DateTime.Now}");
            Console.Error.WriteLine("Process ID: " + System.Diagnostics.Process.GetCurrentProcess().Id);

            try
            {
                using var processor = new CommandProcessor();
                
                // Start processing commands - this blocks until stdin is closed
                processor.StartProcessing();
                
                Console.Error.WriteLine("ETABS Connector shutting down normally");
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Fatal error in ETABS Connector: {ex.Message}");
                Console.Error.WriteLine($"Stack trace: {ex.StackTrace}");
                Environment.Exit(1);
            }
        }
    }
}