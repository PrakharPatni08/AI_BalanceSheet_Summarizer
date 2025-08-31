"""
Enhanced Balance Sheet Analyzer with Advanced AI Insights
This module provides additional AI-powered analysis capabilities
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AdvancedBalanceSheetAnalyzer:
    """Advanced AI analyzer for deeper balance sheet insights"""
    
    def __init__(self):
        self.industry_benchmarks = {
            'current_ratio': {'excellent': 2.0, 'good': 1.5, 'acceptable': 1.0},
            'debt_to_equity': {'excellent': 0.3, 'good': 0.5, 'acceptable': 1.0},
            'asset_turnover': {'excellent': 1.5, 'good': 1.0, 'acceptable': 0.7}
        }
    
    def calculate_advanced_ratios(self, df: pd.DataFrame) -> Dict:
        """Calculate advanced financial ratios"""
        latest_year = [col for col in df.columns if 'Amount_' in col][-1]
        
        # Group data by category
        category_data = df.groupby('Category')[latest_year].sum()
        
        current_assets = abs(category_data.get('Current Assets', 0))
        non_current_assets = abs(category_data.get('Non-Current Assets', 0))
        current_liabilities = abs(category_data.get('Current Liabilities', 0))
        non_current_liabilities = abs(category_data.get('Non-Current Liabilities', 0))
        equity = abs(category_data.get('Equity', 0))
        
        total_assets = current_assets + non_current_assets
        total_liabilities = current_liabilities + non_current_liabilities
        
        ratios = {
            'liquidity_ratios': {
                'current_ratio': current_assets / current_liabilities if current_liabilities > 0 else 0,
                'quick_ratio': (current_assets * 0.8) / current_liabilities if current_liabilities > 0 else 0,
                'cash_ratio': (current_assets * 0.3) / current_liabilities if current_liabilities > 0 else 0
            },
            'leverage_ratios': {
                'debt_to_equity': total_liabilities / equity if equity > 0 else 0,
                'debt_ratio': total_liabilities / total_assets if total_assets > 0 else 0,
                'equity_ratio': equity / total_assets if total_assets > 0 else 0
            },
            'efficiency_ratios': {
                'asset_composition': {
                    'current_assets_ratio': current_assets / total_assets if total_assets > 0 else 0,
                    'fixed_assets_ratio': non_current_assets / total_assets if total_assets > 0 else 0
                }
            }
        }
        
        return ratios
    
    def generate_risk_assessment(self, ratios: Dict) -> Dict:
        """Generate comprehensive risk assessment"""
        
        risk_factors = {
            'liquidity_risk': 'Low',
            'solvency_risk': 'Low',
            'operational_risk': 'Low',
            'overall_risk': 'Low',
            'risk_score': 0  # 0-100 scale
        }
        
        score = 0
        
        # Liquidity Risk Assessment
        current_ratio = ratios.get('liquidity_ratios', {}).get('current_ratio', 0)
        if current_ratio < 1:
            risk_factors['liquidity_risk'] = 'High'
            score += 30
        elif current_ratio < 1.5:
            risk_factors['liquidity_risk'] = 'Medium'
            score += 15
        
        # Solvency Risk Assessment
        debt_to_equity = ratios.get('leverage_ratios', {}).get('debt_to_equity', 0)
        if debt_to_equity > 2:
            risk_factors['solvency_risk'] = 'High'
            score += 25
        elif debt_to_equity > 1:
            risk_factors['solvency_risk'] = 'Medium'
            score += 12
        
        # Overall Risk Score
        risk_factors['risk_score'] = min(score, 100)
        
        if score > 50:
            risk_factors['overall_risk'] = 'High'
        elif score > 25:
            risk_factors['overall_risk'] = 'Medium'
        
        return risk_factors
    
    def generate_recommendations(self, ratios: Dict, risk_assessment: Dict) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Liquidity recommendations
        current_ratio = ratios.get('liquidity_ratios', {}).get('current_ratio', 0)
        if current_ratio < 1:
            recommendations.append("🚨 **Critical**: Improve liquidity immediately by increasing current assets or reducing short-term liabilities")
        elif current_ratio < 1.5:
            recommendations.append("⚠️ **Important**: Consider building cash reserves or extending payment terms with suppliers")
        elif current_ratio > 3:
            recommendations.append("💡 **Optimization**: High liquidity - consider investing excess cash in growth opportunities")
        
        # Leverage recommendations
        debt_to_equity = ratios.get('leverage_ratios', {}).get('debt_to_equity', 0)
        if debt_to_equity > 2:
            recommendations.append("🚨 **Critical**: High leverage poses significant financial risk - consider debt reduction strategies")
        elif debt_to_equity > 1:
            recommendations.append("⚠️ **Monitor**: Moderate leverage - monitor debt service capabilities closely")
        elif debt_to_equity < 0.3:
            recommendations.append("💡 **Growth**: Conservative leverage - potential to use more debt for profitable growth")
        
        # Asset efficiency recommendations
        current_assets_ratio = ratios.get('efficiency_ratios', {}).get('asset_composition', {}).get('current_assets_ratio', 0)
        if current_assets_ratio > 0.7:
            recommendations.append("🔄 **Strategy**: High current assets ratio - evaluate long-term investment opportunities")
        elif current_assets_ratio < 0.3:
            recommendations.append("🔄 **Balance**: Low current assets - ensure adequate working capital for operations")
        
        # Risk-based recommendations
        overall_risk = risk_assessment.get('overall_risk', 'Low')
        if overall_risk == 'High':
            recommendations.append("🚨 **Priority**: High overall risk detected - implement comprehensive financial restructuring plan")
        elif overall_risk == 'Medium':
            recommendations.append("⚠️ **Action**: Moderate risk - develop contingency plans and monitor key metrics closely")
        
        return recommendations
    
    def benchmark_analysis(self, ratios: Dict) -> Dict:
        """Compare ratios against industry benchmarks"""
        
        benchmark_results = {}
        
        # Current Ratio Benchmark
        current_ratio = ratios.get('liquidity_ratios', {}).get('current_ratio', 0)
        if current_ratio >= self.industry_benchmarks['current_ratio']['excellent']:
            benchmark_results['current_ratio'] = {'status': 'Excellent', 'color': 'green'}
        elif current_ratio >= self.industry_benchmarks['current_ratio']['good']:
            benchmark_results['current_ratio'] = {'status': 'Good', 'color': 'yellow'}
        elif current_ratio >= self.industry_benchmarks['current_ratio']['acceptable']:
            benchmark_results['current_ratio'] = {'status': 'Acceptable', 'color': 'orange'}
        else:
            benchmark_results['current_ratio'] = {'status': 'Below Standard', 'color': 'red'}
        
        # Debt-to-Equity Benchmark
        debt_to_equity = ratios.get('leverage_ratios', {}).get('debt_to_equity', 0)
        if debt_to_equity <= self.industry_benchmarks['debt_to_equity']['excellent']:
            benchmark_results['debt_to_equity'] = {'status': 'Excellent', 'color': 'green'}
        elif debt_to_equity <= self.industry_benchmarks['debt_to_equity']['good']:
            benchmark_results['debt_to_equity'] = {'status': 'Good', 'color': 'yellow'}
        elif debt_to_equity <= self.industry_benchmarks['debt_to_equity']['acceptable']:
            benchmark_results['debt_to_equity'] = {'status': 'Acceptable', 'color': 'orange'}
        else:
            benchmark_results['debt_to_equity'] = {'status': 'Above Recommended', 'color': 'red'}
        
        return benchmark_results
