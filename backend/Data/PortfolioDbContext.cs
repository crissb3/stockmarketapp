using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.EntityFrameworkCore;

namespace stockmarketapp_backend.Data;

public class PortfolioDbContext : DbContext
{
    public PortfolioDbContext(DbContextOptions<PortfolioDbContext> options)
        : base(options)
    {
    }

    public DbSet<AssetHistory> AssetHistory { get; set; }
    public DbSet<PortfolioTotals> PortfolioTotals { get; set; }
}

public class AssetHistory
{
    public int Id { get; set; }
    public DateTime DateTime { get; set; }
    public string Symbol { get; set; } = string.Empty;
    [Column("latest_close")]
    public double LatestClose { get; set; }
    public double Value { get; set; }
    public string Currency { get; set; } = string.Empty;
    public double Shares { get; set; }
}

public class PortfolioTotals
{
    public int Id { get; set; }
    public DateTime DateTime { get; set; }
    public string Currency { get; set; } = string.Empty;
    [Column("total_value")]
    public double TotalValue { get; set; }
}
