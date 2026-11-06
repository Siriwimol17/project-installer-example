using DotnetSvc.Endpoints;
using DotnetSvc.Middleware;
using Serilog;

var builder = WebApplication.CreateBuilder(args);

var portValue = Environment.GetEnvironmentVariable("PORT");
var token = Environment.GetEnvironmentVariable("INTERNAL_TOKEN");
var dataDir = Environment.GetEnvironmentVariable("DATA_DIR");
if (!int.TryParse(portValue, out var port) || port is < 1 or > 65535)
{
    Console.Error.WriteLine("Configuration error: PORT is required and must be a valid port (1-65535).");
    Environment.ExitCode = 2;
    return;
}
if (string.IsNullOrWhiteSpace(token))
{
    Console.Error.WriteLine("Configuration error: INTERNAL_TOKEN is required.");
    Environment.ExitCode = 2;
    return;
}
if (string.IsNullOrWhiteSpace(dataDir))
{
    Console.Error.WriteLine("Configuration error: DATA_DIR is required.");
    Environment.ExitCode = 2;
    return;
}

Directory.CreateDirectory(dataDir);
builder.WebHost.UseUrls($"http://127.0.0.1:{port}");
builder.Host.UseSerilog((context, logger) => logger
    .Enrich.FromLogContext()
    .Enrich.WithProperty("Service", "dotnet-svc")
    .WriteTo.Console(outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}"));
builder.Services.AddSingleton(new InternalTokenOptions(token));

var app = builder.Build();
app.UseMiddleware<HostValidationMiddleware>();
app.UseMiddleware<InternalTokenMiddleware>();
app.MapDotnetSvcEndpoints();
app.Run();

public partial class Program;
