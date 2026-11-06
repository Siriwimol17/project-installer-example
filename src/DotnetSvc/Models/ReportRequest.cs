namespace DotnetSvc.Models;

public sealed record ReportItem(string Name, decimal Value);
public sealed record ReportRequest(List<ReportItem>? Items);
public sealed record ReportSummary(int Count, decimal Sum, decimal Average, decimal Min, decimal Max, IReadOnlyList<ReportItem> TopItems);
