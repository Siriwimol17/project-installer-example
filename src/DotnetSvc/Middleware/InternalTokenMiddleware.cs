using System.Security.Cryptography;
using System.Text;

namespace DotnetSvc.Middleware;

public sealed record InternalTokenOptions(string Token);

public sealed class InternalTokenMiddleware(RequestDelegate next, InternalTokenOptions options)
{
    public async Task InvokeAsync(HttpContext context)
    {
        if (HttpMethods.IsGet(context.Request.Method) && context.Request.Path == "/health")
        {
            await next(context);
            return;
        }

        var provided = context.Request.Headers["X-Internal-Token"].ToString();
        var expectedBytes = Encoding.UTF8.GetBytes(options.Token);
        var providedBytes = Encoding.UTF8.GetBytes(provided);
        if (providedBytes.Length != expectedBytes.Length || !CryptographicOperations.FixedTimeEquals(providedBytes, expectedBytes))
        {
            context.Response.StatusCode = StatusCodes.Status401Unauthorized;
            await context.Response.WriteAsJsonAsync(new { error = "unauthorized" });
            return;
        }

        await next(context);
    }
}
