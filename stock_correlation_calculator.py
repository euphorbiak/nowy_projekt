"""
Stock Correlation Calculator for 1000 US Listed Stocks

This module provides tools to calculate pairwise correlations between US listed stocks,
efficiently handling large datasets and generating correlation matrices and visualizations.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockCorrelationCalculator:
    """Calculate pairwise correlations for a large set of US stocks."""
    
    def __init__(self, cache_dir: str = "./cache"):
        """
        Initialize the correlation calculator.
        
        Args:
            cache_dir: Directory to cache stock data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.stock_data = None
        self.correlation_matrix = None
        self.returns_data = None
        
    def load_stock_list(self, symbols: Optional[List[str]] = None) -> List[str]:
        """
        Load list of stock symbols.
        
        Args:
            symbols: List of stock symbols. If None, loads common US stocks.
            
        Returns:
            List of valid stock symbols
        """
        if symbols is None:
            # Load popular US stocks (can be customized)
            symbols = self._get_default_us_stocks()
        
        logger.info(f"Loaded {len(symbols)} stock symbols")
        return symbols
    
    def _get_default_us_stocks(self) -> List[str]:
        """Get default list of popular US stocks."""
        # Popular US stocks across different sectors
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BERKB',
            'JPM', 'JNJ', 'V', 'WMT', 'PG', 'MA', 'HD', 'INTC', 'CSCO', 'VZ',
            'MRK', 'NFLX', 'COST', 'ADBE', 'CRM', 'DIS', 'CMCSA', 'PYPL',
            'TXN', 'QCOM', 'AVGO', 'CISCO', 'AMAT', 'MU', 'KLAC', 'SNPS',
            'SPLK', 'OKTA', 'DATADOG', 'CRWD', 'ZM', 'DOCU', 'DOCN', 'DBX',
            'BOX', 'NET', 'FASTLY', 'DDOG', 'MNST', 'ETSY', 'SHOP', 'ROKU',
            'SQ', 'DASH', 'UBER', 'LYFT', 'ZS', 'PANW', 'PALO', 'PLTR',
            'RIOT', 'MARA', 'COIN', 'GME', 'AMC', 'BB', 'NOK', 'F', 'GM',
            'TM', 'HMC', 'GE', 'BA', 'LMT', 'RTX', 'NOC', 'LDOS', 'XYL',
            'EATON', 'PH', 'ROK', 'EMR', 'CARR', 'IEX', 'CPRI', 'MTH',
            # Add more symbols as needed to reach 1000
        ]
    
    def download_stock_data(
        self, 
        symbols: List[str], 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "2y",
        max_workers: int = 10
    ) -> pd.DataFrame:
        """
        Download historical stock data for given symbols.
        
        Args:
            symbols: List of stock symbols
            start_date: Start date (format: 'YYYY-MM-DD'). If None, uses period.
            end_date: End date (format: 'YYYY-MM-DD'). Defaults to today.
            period: Period if start_date not specified (e.g., '2y', '5y')
            max_workers: Number of parallel workers for download
            
        Returns:
            DataFrame with adjusted close prices
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Downloading data for {len(symbols)} stocks from {start_date} to {end_date}")
        
        downloaded_data = {}
        failed_symbols = []
        
        def download_single_stock(symbol: str) -> Tuple[str, Optional[pd.Series]]:
            try:
                data = yf.download(symbol, start=start_date, end=end_date, progress=False)
                if data.empty:
                    return symbol, None
                return symbol, data['Adj Close']
            except Exception as e:
                logger.warning(f"Failed to download {symbol}: {e}")
                return symbol, None
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(download_single_stock, sym): sym for sym in symbols}
            
            for i, future in enumerate(as_completed(futures)):
                symbol, data = future.result()
                if data is not None:
                    downloaded_data[symbol] = data
                else:
                    failed_symbols.append(symbol)
                
                if (i + 1) % 50 == 0:
                    logger.info(f"Downloaded {i + 1}/{len(symbols)} stocks")
        
        # Combine data into a single DataFrame
        self.stock_data = pd.DataFrame(downloaded_data)
        
        # Remove rows with missing values
        self.stock_data = self.stock_data.dropna()
        
        logger.info(f"Successfully downloaded {len(self.stock_data.columns)} stocks")
        logger.info(f"Failed to download {len(failed_symbols)} stocks")
        
        return self.stock_data
    
    def calculate_returns(self, method: str = 'log') -> pd.DataFrame:
        """
        Calculate returns from price data.
        
        Args:
            method: 'log' for logarithmic returns, 'simple' for simple returns
            
        Returns:
            DataFrame with returns
        """
        if self.stock_data is None:
            raise ValueError("No stock data loaded. Call download_stock_data first.")
        
        if method == 'log':
            self.returns_data = np.log(self.stock_data / self.stock_data.shift(1))
        else:
            self.returns_data = self.stock_data.pct_change()
        
        # Remove NaN values from first row
        self.returns_data = self.returns_data.dropna()
        
        logger.info(f"Calculated {method} returns for {self.returns_data.shape[1]} stocks")
        
        return self.returns_data
    
    def calculate_correlation_matrix(
        self,
        method: str = 'pearson'
    ) -> pd.DataFrame:
        """
        Calculate pairwise correlation matrix.
        
        Args:
            method: 'pearson', 'kendall', or 'spearman'
            
        Returns:
            Correlation matrix
        """
        if self.returns_data is None:
            self.calculate_returns()
        
        logger.info(f"Calculating {method} correlation matrix...")
        self.correlation_matrix = self.returns_data.corr(method=method)
        
        logger.info("Correlation matrix calculated")
        return self.correlation_matrix
    
    def get_top_correlations(
        self,
        n: int = 20,
        exclude_diagonal: bool = True
    ) -> pd.DataFrame:
        """
        Get top N highest correlations.
        
        Args:
            n: Number of top correlations to return
            exclude_diagonal: Whether to exclude correlation with self
            
        Returns:
            DataFrame with top correlations
        """
        if self.correlation_matrix is None:
            self.calculate_correlation_matrix()
        
        # Convert correlation matrix to long format
        corr_pairs = []
        
        for i in range(len(self.correlation_matrix.columns)):
            for j in range(i + 1, len(self.correlation_matrix.columns)):
                symbol1 = self.correlation_matrix.columns[i]
                symbol2 = self.correlation_matrix.columns[j]
                corr = self.correlation_matrix.iloc[i, j]
                
                corr_pairs.append({
                    'Stock1': symbol1,
                    'Stock2': symbol2,
                    'Correlation': corr
                })
        
        corr_df = pd.DataFrame(corr_pairs)
        corr_df = corr_df.sort_values('Correlation', key=abs, ascending=False)
        
        return corr_df.head(n)
    
    def get_lowest_correlations(
        self,
        n: int = 20
    ) -> pd.DataFrame:
        """
        Get top N lowest correlations (most negative).
        
        Args:
            n: Number of lowest correlations to return
            
        Returns:
            DataFrame with lowest correlations
        """
        if self.correlation_matrix is None:
            self.calculate_correlation_matrix()
        
        corr_pairs = []
        
        for i in range(len(self.correlation_matrix.columns)):
            for j in range(i + 1, len(self.correlation_matrix.columns)):
                symbol1 = self.correlation_matrix.columns[i]
                symbol2 = self.correlation_matrix.columns[j]
                corr = self.correlation_matrix.iloc[i, j]
                
                corr_pairs.append({
                    'Stock1': symbol1,
                    'Stock2': symbol2,
                    'Correlation': corr
                })
        
        corr_df = pd.DataFrame(corr_pairs)
        corr_df = corr_df.sort_values('Correlation', ascending=True)
        
        return corr_df.head(n)
    
    def save_results(self, filename: str = "correlation_results.pkl"):
        """
        Save correlation results to file.
        
        Args:
            filename: Output filename
        """
        results = {
            'stock_data': self.stock_data,
            'returns_data': self.returns_data,
            'correlation_matrix': self.correlation_matrix
        }
        
        filepath = self.cache_dir / filename
        
        with open(filepath, 'wb') as f:
            pickle.dump(results, f)
        
        logger.info(f"Results saved to {filepath}")
    
    def load_results(self, filename: str = "correlation_results.pkl"):
        """
        Load correlation results from file.
        
        Args:
            filename: Input filename
        """
        filepath = self.cache_dir / filename
        
        with open(filepath, 'rb') as f:
            results = pickle.load(f)
        
        self.stock_data = results['stock_data']
        self.returns_data = results['returns_data']
        self.correlation_matrix = results['correlation_matrix']
        
        logger.info(f"Results loaded from {filepath}")
    
    def get_correlation_stats(self) -> dict:
        """
        Get statistics about the correlation matrix.
        
        Returns:
            Dictionary with correlation statistics
        """
        if self.correlation_matrix is None:
            self.calculate_correlation_matrix()
        
        # Extract upper triangle to avoid duplicates and diagonal
        upper_triangle = self.correlation_matrix.values[
            np.triu_indices_from(self.correlation_matrix.values, k=1)
        ]
        
        stats = {
            'mean_correlation': float(np.mean(upper_triangle)),
            'median_correlation': float(np.median(upper_triangle)),
            'std_correlation': float(np.std(upper_triangle)),
            'min_correlation': float(np.min(upper_triangle)),
            'max_correlation': float(np.max(upper_triangle)),
            'num_stocks': len(self.correlation_matrix.columns),
            'num_pairs': len(upper_triangle)
        }
        
        return stats


if __name__ == "__main__":
    # Example usage
    calculator = StockCorrelationCalculator()
    
    # Load default US stocks
    symbols = calculator.load_stock_list()
    
    # Download stock data
    stock_data = calculator.download_stock_data(symbols)
    
    # Calculate returns
    returns = calculator.calculate_returns(method='log')
    
    # Calculate correlation matrix
    corr_matrix = calculator.calculate_correlation_matrix(method='pearson')
    
    # Get correlation statistics
    stats = calculator.get_correlation_stats()
    print("\nCorrelation Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get top correlations
    print("\nTop 20 Highest Correlations:")
    top_corr = calculator.get_top_correlations(n=20)
    print(top_corr)
    
    # Get lowest correlations
    print("\nTop 20 Lowest Correlations:")
    lowest_corr = calculator.get_lowest_correlations(n=20)
    print(lowest_corr)
    
    # Save results
    calculator.save_results()
