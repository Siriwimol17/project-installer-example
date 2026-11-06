using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Xunit;

namespace DotnetSvc.Tests;

public sealed class DotnetSvcApiTests : IClassFixture<DotnetSvcFactory>
{
    private readonly HttpClient _client;

    public DotnetSvcApiTests(DotnetSvcFactory factory)
    {
        _client = factory.CreateClient();
        _client.DefaultRequestHeaders.Host = "127.0.0.1";
    }

    [Fact]
    public async Task HealthDoesNotRequireToken()
    {
        var response = await _client.GetAsync("/health");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Contains("dotnet-svc", await response.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task HelloRequiresToken()
    {
        Assert.Equal(HttpStatusCode.Unauthorized, (await _client.GetAsync("/api/hello")).StatusCode);
        using var authorized = new HttpRequestMessage(HttpMethod.Get, "/api/hello");
        authorized.Headers.Add("X-Internal-Token", "dev-token");
        Assert.Equal(HttpStatusCode.OK, (await _client.SendAsync(authorized)).StatusCode);
    }

    [Fact]
    public async Task ReportReturnsSummary()
    {
        using var request = new HttpRequestMessage(HttpMethod.Post, "/api/report")
        {
            Content = JsonContent.Create(new { items = new[] { new { name = "a", value = 10 }, new { name = "b", value = 20 } } })
        };
        request.Headers.Add("X-Internal-Token", "dev-token");
        var response = await _client.SendAsync(request);
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var json = await response.Content.ReadAsStringAsync();
        Assert.Contains("\"count\":2", json);
        Assert.Contains("\"sum\":30", json);
    }

    [Fact]
    public async Task ReportRejectsEmptyItems()
    {
        using var request = new HttpRequestMessage(HttpMethod.Post, "/api/report")
        {
            Content = JsonContent.Create(new { items = Array.Empty<object>() })
        };
        request.Headers.Add("X-Internal-Token", "dev-token");
        Assert.Equal(HttpStatusCode.BadRequest, (await _client.SendAsync(request)).StatusCode);
    }
}

public sealed class DotnetSvcFactory : WebApplicationFactory<Program>
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureAppConfiguration((_, config) => config.AddInMemoryCollection(new Dictionary<string, string?>
        {
            ["PORT"] = "5101", ["INTERNAL_TOKEN"] = "dev-token", ["DATA_DIR"] = Path.GetTempPath()
        }));
        Environment.SetEnvironmentVariable("PORT", "5101");
        Environment.SetEnvironmentVariable("INTERNAL_TOKEN", "dev-token");
        Environment.SetEnvironmentVariable("DATA_DIR", Path.GetTempPath());
    }
}
 

