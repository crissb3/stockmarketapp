using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using stockmarketapp_backend.Data;

namespace stockmarketapp_backend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PortfolioController : ControllerBase
{
    private readonly PortfolioDbContext _db;
    private readonly ILogger<PortfolioController> _logger;
    
    public PortfolioController(PortfolioDbContext db,  ILogger<PortfolioController> logger)
    {
        _db = db;
        _logger = logger;
    }

    [HttpGet("assets")]
    public async Task<IActionResult> GetAssets()
    {
        try
        {
            var assets = await _db.AssetHistory
                .OrderByDescending(a => a.DateTime)
                .ToListAsync();
            
            return  Ok(assets);
        }
        catch (Exception e)
        {
            _logger.LogError(e.Message);
            return StatusCode(500);
        }
    }
    
    [HttpGet("totals")]
    public async Task<IActionResult> GetTotals()
    {
        try
        {
            var totals = await _db.PortfolioTotals
                .OrderByDescending(a => a.DateTime)
                .ToListAsync();
            
            return  Ok(totals);
        }
        catch (Exception e)
        {
            _logger.LogError(e.Message);
            return StatusCode(500);
        }
    }

    [HttpGet("latest")]
    public async Task<IActionResult> GetLatestPerAsset()
    {
        try
        {
            var latestAssets = await _db.AssetHistory
                .GroupBy(a => a.Symbol)
                .Select(g => g.OrderByDescending(a => a.DateTime).First())
                .ToListAsync();
            
            return Ok(latestAssets);
        }
        catch (Exception e)
        {
            _logger.LogError(e.Message);
            return StatusCode(500);
        }
    }
    
}