"""
Utilities for data processing and validation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import re

class DataValidator:
    """Validates and processes balance sheet data"""
    
    @staticmethod
    def validate_balance_sheet(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate balance sheet data format and content"""
        
        errors = []
        
        # Check required columns
        required_columns = ['Account', 'Category']
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")
        
        # Check for amount columns
        amount_columns = [col for col in df.columns if 'Amount_' in col or col.lower().startswith('amount')]
        if not amount_columns:
            errors.append("No amount columns found. Expected columns like 'Amount_2023', 'Amount_2022', etc.")
        
        # Check for valid categories
        if 'Category' in df.columns:
            valid_categories = ['Current Assets', 'Non-Current Assets', 'Current Liabilities', 
                              'Non-Current Liabilities', 'Equity', 'Assets', 'Liabilities']
            invalid_categories = set(df['Category'].unique()) - set(valid_categories)
            if invalid_categories:
                errors.append(f"Invalid categories found: {list(invalid_categories)}")
        
        # Check for numeric data in amount columns
        for col in amount_columns:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='coerce')
                except:
                    errors.append(f"Non-numeric data found in column: {col}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def standardize_categories(df: pd.DataFrame) -> pd.DataFrame:
        """Standardize category names"""
        
        category_mapping = {
            'current assets': 'Current Assets',
            'current_assets': 'Current Assets',
            'short-term assets': 'Current Assets',
            'non-current assets': 'Non-Current Assets',
            'non_current_assets': 'Non-Current Assets',
            'long-term assets': 'Non-Current Assets',
            'fixed assets': 'Non-Current Assets',
            'current liabilities': 'Current Liabilities',
            'current_liabilities': 'Current Liabilities',
            'short-term liabilities': 'Current Liabilities',
            'non-current liabilities': 'Non-Current Liabilities',
            'non_current_liabilities': 'Non-Current Liabilities',
            'long-term liabilities': 'Non-Current Liabilities',
            'equity': 'Equity',
            'shareholders equity': 'Equity',
            'stockholders equity': 'Equity'
        }
        
        if 'Category' in df.columns:
            df['Category'] = df['Category'].str.lower().map(category_mapping).fillna(df['Category'])
        
        return df
    
    @staticmethod
    def clean_financial_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare financial data"""
        
        # Remove any rows with all NaN values
        df = df.dropna(how='all')
        
        # Clean account names
        if 'Account' in df.columns:
            df['Account'] = df['Account'].str.strip()
        
        # Handle amount columns
        amount_columns = [col for col in df.columns if 'Amount_' in col or col.lower().startswith('amount')]
        for col in amount_columns:
            if col in df.columns:
                # Convert to numeric, handling any string formatting
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('$', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Fill NaN values with 0
                df[col] = df[col].fillna(0)
        
        return df

class ReportGenerator:
    """Generates various types of reports"""
    
    @staticmethod
    def generate_executive_summary(analysis: Dict, insights: List[str]) -> str:
        """Generate executive summary text"""
        
        if not analysis.get('ratios'):
            return "Insufficient data for executive summary generation."
        
        latest_year = max(analysis['ratios'].keys()) if analysis.get('ratios') else 'Unknown'
        ratios = analysis['ratios'].get(latest_year, {})
        
        summary_parts = [
            f"# Executive Summary - Financial Year {latest_year}",
            "",
            "## Financial Position Overview",
            f"- **Liquidity Position**: Current Ratio of {ratios.get('current_ratio', 0):.2f}",
            f"- **Leverage Position**: Debt-to-Equity Ratio of {ratios.get('debt_to_equity', 0):.2f}",
            f"- **Total Assets**: ${ratios.get('totals', {}).get('total_assets', 0):,.0f}",
            "",
            "## Key Insights",
        ]
        
        for i, insight in enumerate(insights[:5], 1):
            clean_insight = insight.split('**')[-1] if '**' in insight else insight
            summary_parts.append(f"{i}. {clean_insight}")
        
        if analysis.get('trends'):
            summary_parts.extend([
                "",
                "## Year-over-Year Trends",
                f"- Current Ratio Change: {analysis['trends'].get('current_ratio_change', 0):+.2f}",
                f"- Total Assets Growth: {analysis['trends'].get('total_assets_change_pct', 0):+.1f}%"
            ])
        
        return "\n".join(summary_parts)
    
    @staticmethod
    def create_ratio_summary_table(ratios: Dict) -> pd.DataFrame:
        """Create a summary table of financial ratios"""
        
        ratio_data = []
        
        for year, year_ratios in ratios.items():
            ratio_data.append({
                'Year': year,
                'Current_Ratio': year_ratios.get('current_ratio', 0),
                'Debt_to_Equity': year_ratios.get('debt_to_equity', 0),
                'Total_Assets': year_ratios.get('totals', {}).get('total_assets', 0),
                'Total_Liabilities': year_ratios.get('totals', {}).get('total_liabilities', 0),
                'Total_Equity': year_ratios.get('totals', {}).get('total_equity', 0)
            })
        
        return pd.DataFrame(ratio_data)

class ChartGenerator:
    """Generate additional chart configurations"""
    
    @staticmethod
    def get_color_scheme() -> Dict:
        """Return consistent color scheme for charts"""
        return {
            'assets': '#2E86AB',
            'liabilities': '#A23B72',
            'equity': '#F18F01',
            'positive': '#2E8B57',
            'negative': '#DC143C',
            'neutral': '#708090'
        }
    
    @staticmethod
    def format_currency(value: float) -> str:
        """Format currency values for display"""
        if abs(value) >= 1_000_000:
            return f"${value/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            return f"${value/1_000:.1f}K"
        else:
            return f"${value:.0f}"
