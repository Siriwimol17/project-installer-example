using DotnetSvc.Models;

namespace DotnetSvc.Endpoints;

public static class DotnetSvcEndpoints
{
    public static IEndpointRouteBuilder MapDotnetSvcEndpoints(this IEndpointRouteBuilder endpoints)
    {
        endpoints.MapGet("/health", () => Results.Ok(new { status = "ok", service = "dotnet-svc" }));
        endpoints.MapPost("/shutdown", (IHostApplicationLifetime lifetime) =>
        {
            lifetime.StopApplication();
            return Results.Accepted();
        });
        endpoints.MapGet("/api/hello", () => Results.Ok(new { message = "Hello from DotnetSvc", time = DateTimeOffset.UtcNow }));
        endpoints.MapPost("/api/report", (ReportRequest? request) =>
        {
            if (request?.Items is not { Count: > 0 } items || items.Any(item => item is null || string.IsNullOrWhiteSpace(item.Name)))
                return Results.BadRequest(new { error = "items must contain at least one item with a name." });

            var values = items.Select(item => item.Value).ToArray();
            var summary = new ReportSummary(items.Count, values.Sum(), values.Average(), values.Min(), values.Max(),
                items.OrderByDescending(item => item.Value).ThenBy(item => item.Name, StringComparer.Ordinal).Take(3).ToArray());
            return Results.Ok(summary);
        });
        return endpoints;
    }
}
