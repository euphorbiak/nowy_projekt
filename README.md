```markdown
# Stock Correlation Calculator 📈

A powerful tool for analyzing stock market correlations. Perfect for portfolio managers, quantitative analysts, and investors.

## What Does It Do?

This tool calculates how similar stocks move together by:
- **Downloading** historical price data for up to 1000 US stocks
- **Calculating** correlation coefficients between all stock pairs
- **Analyzing** patterns to find:
  - Stocks that move together (high correlation)
  - Stocks that move independently (low correlation - good for diversification)

## Quick Features

✅ Handles 1000+ stocks simultaneously  
✅ Fast parallel data downloads  
✅ Multiple correlation methods (Pearson, Kendall, Spearman)  
✅ Find best stocks for portfolio diversification  
✅ Sector-by-sector analysis  
✅ Save and reload results  

## Getting Started

### Installation (For Developers)

```bash
# 1. Download this project
git clone https://github.com/euphorbiak/nowy_projekt.git
cd nowy_projekt

# 2. Install required packages
pip install -r requirements.txt

# 3. Run the tool
python stock_correlation_calculator.py
```

### Basic Usage

```python
from stock_correlation_calculator import StockCorrelationCalculator

# Create a calculator
calc = StockCorrelationCalculator()

# Pick your stocks
stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Download price data (last 2 years)
calc.download_stock_data(stocks, period='2y')

# Calculate returns
calc.calculate_returns(method='log')

# Calculate correlations
calc.calculate_correlation_matrix()

# Get statistics
stats = calc.get_correlation_stats()
print(f"Average correlation: {stats['mean_correlation']}")
```

## What is Correlation?

**Correlation** measures how much two stocks move together:
- **+1.0** = Move perfectly together
- **0.0** = Move independently
- **-1.0** = Move in opposite directions

### Example:
- Apple and Microsoft might have correlation of **0.7** (they both move with tech sector)
- Apple and Oil company might have correlation of **0.2** (they move separately)

## Use Cases

### 1. Build a Diversified Portfolio
```python
calc = StockCorrelationCalculator()
calc.download_stock_data(my_stocks)
calc.calculate_returns()
calc.calculate_correlation_matrix()

# Find uncorrelated pairs
best_pairs = calc.get_lowest_correlations(n=20)
```

### 2. Analyze a Sector
```python
tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVIDIA']
calc.download_stock_data(tech_stocks)
# See how tightly these stocks move together
```

### 3. Compare Different Time Periods
```python
# Last 1 year
calc.download_stock_data(stocks, period='1y')
short_term_corr = calc.calculate_correlation_matrix()

# Last 5 years  
calc.download_stock_data(stocks, period='5y')
long_term_corr = calc.calculate_correlation_matrix()
```

## Main Functions

### Download Stock Data
```python
calc.download_stock_data(
    symbols=['AAPL', 'MSFT'],  # Stock ticker symbols
    period='2y',               # '1y', '2y', '5y', etc.
    max_workers=10             # More = faster (but uses more internet)
)
```

### Calculate Returns
```python
calc.calculate_returns(
    method='log'  # Use 'log' or 'simple'
)
```

### Calculate Correlations
```python
calc.calculate_correlation_matrix(
    method='pearson'  # Also: 'kendall', 'spearman'
)
```

### Get Results
```python
# Overall statistics
stats = calc.get_correlation_stats()

# Top 20 most correlated pairs
top = calc.get_top_correlations(n=20)

# Top 20 least correlated pairs (for diversification)
bottom = calc.get_lowest_correlations(n=20)

# Full correlation matrix
matrix = calc.correlation_matrix
```

### Save Your Work
```python
# Save to disk (so you don't have to download again)
calc.save_results('my_analysis.pkl')

# Load later
calc.load_results('my_analysis.pkl')
```

## Common Stock Symbols

### Technology
AAPL, MSFT, GOOGL, META, NVDA, INTC, AMD, QCOM

### Finance  
JPM, BAC, WFC, GS, MS, C, BK, USB

### Healthcare
JNJ, PFE, MRK, AZN, ABBV, LLY, UNH, CVS

### Retail
WMT, COST, HD, DIS, AMZN, MCD, KO, NKE

### Energy
XOM, CVX, COP, MPC, PSX, VLO, EOG, SLB

## Troubleshooting

**Problem:** Download fails for some stocks  
**Solution:** The tool skips stocks that fail. This is normal. Check logs for details.

**Problem:** Takes too long to download  
**Solution:** Increase `max_workers=20` or `max_workers=30`

**Problem:** Memory error with 1000 stocks  
**Solution:** Process in smaller batches (100-200 stocks at a time)

**Problem:** Getting an error about "yfinance"  
**Solution:** Run `pip install --upgrade yfinance`

## System Requirements

- Python 3.8 or higher
- Internet connection (to download stock data)
- 2GB+ RAM (for large analyses)

## What's Inside This Repository

```
nowy_projekt/
├── stock_correlation_calculator.py    # Main tool (Python code)
├── app.py                             # Web interface (optional)
├── example_usage.py                   # Examples showing how to use it
├── requirements.txt                   # List of packages needed
├── README.md                          # This file
└── docs/                              # Website files
```

## Dependencies

This tool uses:
- **pandas** - for data handling
- **numpy** - for math operations
- **yfinance** - to download stock prices
- **scipy** - for advanced statistics
- **matplotlib** - for charts (optional)
- **seaborn** - for pretty charts (optional)

All automatically installed with `pip install -r requirements.txt`

## Advanced Features

### Running the Web Server (Optional)
If you want to run a website interface:

```bash
pip install flask
python app.py
```

Then visit: http://localhost:5000

### Parallel Processing
The tool downloads multiple stocks at the same time:

```python
# Slow (downloads 1 at a time)
calc.download_stock_data(stocks, max_workers=1)

# Fast (downloads 20 at a time)
calc.download_stock_data(stocks, max_workers=20)
```

### Different Correlation Methods

**Pearson** (default)
- Most common
- Works best with normally distributed data
- Measures linear relationships

**Spearman**
- Based on rankings
- Better with non-linear relationships
- More robust to outliers

**Kendall**
- Also rank-based
- Good for smaller datasets

## FAQ

**Q: Is this real financial advice?**  
A: No! This is just a tool for analysis. Always consult a financial advisor.

**Q: Can I use this for trading?**  
A: You can use correlations in trading strategies, but test carefully first.

**Q: How often should I update the data?**  
A: That depends on your needs. Daily? Weekly? Monthly?

**Q: Can I add my own stocks?**  
A: Yes! Any valid stock ticker symbol works.

## Next Steps

1. **Try the basic example** - Run `python example_usage.py`
2. **Load your favorite stocks** - Create your own analysis
3. **Save the results** - Use `save_results()` for later
4. **Explore the functions** - Read `stock_correlation_calculator.py` to learn more

## Contributing

Found a bug or have an idea? Open an issue or submit a pull request!

## License

This project is open source - free to use and modify.

---

**Happy analyzing! 📊**

For questions or issues, visit the [GitHub Issues page](https://github.com/euphorbiak/nowy_projekt/issues)
