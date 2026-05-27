from flask import Flask, render_template, request, jsonify
import json
from stock_correlation_calculator import StockCorrelationCalculator

app = Flask(__name__)

# Store calculator instance
calc = None

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/download', methods=['POST'])
def download_stocks():
    """Download stock data"""
    global calc
    try:
        data = request.json
        symbols = data.get('symbols', [])
        period = data.get('period', '2y')
        
        calc = StockCorrelationCalculator()
        calc.download_stock_data(symbols, period=period, max_workers=10)
        
        return jsonify({
            'status': 'success',
            'message': f'Downloaded data for {len(symbols)} stocks'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Calculate correlations"""
    global calc
    try:
        if calc is None:
            return jsonify({
                'status': 'error',
                'message': 'No data loaded. Download stocks first.'
            }), 400
        
        data = request.json
        method = data.get('method', 'pearson')
        
        calc.calculate_returns()
        calc.calculate_correlation_matrix(method=method)
        
        return jsonify({
            'status': 'success',
            'message': 'Correlation matrix calculated'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get correlation statistics"""
    global calc
    try:
        if calc is None or calc.correlation_matrix is None:
            return jsonify({
                'status': 'error',
                'message': 'No calculations performed yet'
            }), 400
        
        stats = calc.get_correlation_stats()
        return jsonify({
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/top-correlations', methods=['GET'])
def top_correlations():
    """Get top correlations"""
    global calc
    try:
        if calc is None or calc.correlation_matrix is None:
            return jsonify({
                'status': 'error',
                'message': 'No calculations performed yet'
            }), 400
        
        n = request.args.get('n', 20, type=int)
        top = calc.get_top_correlations(n=n)
        
        return jsonify({
            'status': 'success',
            'data': top
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/api/lowest-correlations', methods=['GET'])
def lowest_correlations():
    """Get lowest correlations (for diversification)"""
    global calc
    try:
        if calc is None or calc.correlation_matrix is None:
            return jsonify({
                'status': 'error',
                'message': 'No calculations performed yet'
            }), 400
        
        n = request.args.get('n', 20, type=int)
        lowest = calc.get_lowest_correlations(n=n)
        
        return jsonify({
            'status': 'success',
            'data': lowest
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
