"""
Intelligent Balance Sheet Parser - Works with any balance sheet format
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import re

class IntelligentBalanceSheetParser:
    """Smart parser that can handle various balance sheet formats"""
    
    def __init__(self):
        # Extended keyword mappings for intelligent categorization
        self.asset_keywords = [
            'cash', 'bank', 'receivable', 'inventory', 'stock', 'prepaid', 'deposits',
            'property', 'equipment', 'building', 'land', 'machinery', 'vehicle',
            'investment', 'securities', 'bonds', 'goodwill', 'patent', 'trademark',
            'intangible', 'asset', 'deferred tax asset', 'notes receivable'
        ]
        
        self.liability_keywords = [
            'payable', 'debt', 'loan', 'borrowing', 'mortgage', 'bond payable',
            'accrued', 'provision', 'reserve', 'liability', 'obligation',
            'deferred tax liability', 'notes payable', 'overdraft', 'credit line'
        ]
        
        self.equity_keywords = [
            'equity', 'capital', 'stock', 'share', 'retained earnings', 'reserves',
            'surplus', 'accumulated', 'paid-in', 'additional paid', 'treasury stock',
            'comprehensive income', 'revaluation', 'translation adjustment'
        ]
        
        self.current_keywords = [
            'current', 'short-term', 'short term', 'within one year', '< 1 year',
            'less than one year', 'due within', 'maturing within'
        ]
        
        self.non_current_keywords = [
            'non-current', 'non current', 'long-term', 'long term', 'fixed',
            'property plant equipment', 'ppe', 'goodwill', 'intangible'
        ]
    
    def detect_balance_sheet_format(self, df: pd.DataFrame) -> Dict:
        """Analyze and detect the balance sheet format"""
        
        format_info = {
            'format_type': 'unknown',
            'has_categories': False,
            'amount_columns': [],
            'account_column': None,
            'category_column': None,
            'total_rows': [],
            'structure': 'unknown'
        }
        
        # Detect columns
        columns = df.columns.tolist()
        
        # Find account names column
        account_candidates = ['account', 'item', 'description', 'line_item', 'particulars']
        for col in columns:
            if any(keyword in col.lower() for keyword in account_candidates):
                format_info['account_column'] = col
                break
        
        # If no explicit account column, use first text column
        if not format_info['account_column']:
            for col in columns:
                if df[col].dtype == 'object':
                    format_info['account_column'] = col
                    break
        
        # Find category column
        category_candidates = ['category', 'type', 'classification', 'group', 'section']
        for col in columns:
            if any(keyword in col.lower() for keyword in category_candidates):
                format_info['category_column'] = col
                format_info['has_categories'] = True
                break
        
        # Find amount columns (numeric columns or columns with year/amount keywords)
        for col in columns:
            if (df[col].dtype in ['int64', 'float64'] or 
                any(keyword in col.lower() for keyword in ['amount', '202', '201', '200', 'value', 'balance', '$'])):
                format_info['amount_columns'].append(col)
        
        # Detect structure type
        if format_info['has_categories']:
            format_info['format_type'] = 'categorized'
        elif self._detect_traditional_format(df, format_info['account_column']):
            format_info['format_type'] = 'traditional'
        else:
            format_info['format_type'] = 'flat_list'
        
        return format_info
    
    def _detect_traditional_format(self, df: pd.DataFrame, account_col: str) -> bool:
        """Detect if it's a traditional balance sheet format with ASSETS, LIABILITIES, EQUITY headers"""
        
        if not account_col:
            return False
        
        accounts = df[account_col].str.lower().fillna('').tolist()
        headers = ['assets', 'liabilities', 'equity', 'stockholders equity', 'shareholders equity']
        
        return any(any(header in account for header in headers) for account in accounts)
    
    def intelligent_categorization(self, df: pd.DataFrame, format_info: Dict) -> pd.DataFrame:
        """Intelligently categorize balance sheet items"""
        
        df_processed = df.copy()
        account_col = format_info['account_column']
        
        if not account_col:
            return df_processed
        
        # Create category column if it doesn't exist
        if not format_info['has_categories']:
            df_processed['AI_Category'] = df_processed[account_col].apply(self._classify_account)
            format_info['category_column'] = 'AI_Category'
        
        # Standardize existing categories
        if format_info['category_column']:
            df_processed[format_info['category_column']] = df_processed[format_info['category_column']].apply(
                self._standardize_category
            )
        
        return df_processed
    
    def _classify_account(self, account_name: str) -> str:
        """Classify account based on keywords"""
        
        if pd.isna(account_name):
            return 'Unknown'
        
        account_lower = str(account_name).lower()
        
        # Check for equity first (most specific)
        if any(keyword in account_lower for keyword in self.equity_keywords):
            return 'Equity'
        
        # Check for liabilities
        if any(keyword in account_lower for keyword in self.liability_keywords):
            # Determine if current or non-current
            if any(keyword in account_lower for keyword in self.current_keywords):
                return 'Current Liabilities'
            elif any(keyword in account_lower for keyword in self.non_current_keywords):
                return 'Non-Current Liabilities'
            else:
                # Default classification based on common patterns
                if any(term in account_lower for term in ['payable', 'accrued', 'short']):
                    return 'Current Liabilities'
                else:
                    return 'Non-Current Liabilities'
        
        # Check for assets
        if any(keyword in account_lower for keyword in self.asset_keywords):
            # Determine if current or non-current
            if any(keyword in account_lower for keyword in self.current_keywords):
                return 'Current Assets'
            elif any(keyword in account_lower for keyword in self.non_current_keywords):
                return 'Non-Current Assets'
            else:
                # Default classification based on common patterns
                if any(term in account_lower for term in ['cash', 'receivable', 'inventory', 'prepaid']):
                    return 'Current Assets'
                else:
                    return 'Non-Current Assets'
        
        # Default classification based on context
        if 'total' in account_lower:
            return 'Total'
        
        return 'Unknown'
    
    def _standardize_category(self, category: str) -> str:
        """Standardize category names"""
        
        if pd.isna(category):
            return 'Unknown'
        
        category_lower = str(category).lower().strip()
        
        # Mapping for standardization
        category_map = {
            'current assets': 'Current Assets',
            'current asset': 'Current Assets',
            'short term assets': 'Current Assets',
            'short-term assets': 'Current Assets',
            'liquid assets': 'Current Assets',
            
            'non current assets': 'Non-Current Assets',
            'non-current assets': 'Non-Current Assets',
            'long term assets': 'Non-Current Assets',
            'long-term assets': 'Non-Current Assets',
            'fixed assets': 'Non-Current Assets',
            'capital assets': 'Non-Current Assets',
            
            'current liabilities': 'Current Liabilities',
            'current liability': 'Current Liabilities',
            'short term liabilities': 'Current Liabilities',
            'short-term liabilities': 'Current Liabilities',
            
            'non current liabilities': 'Non-Current Liabilities',
            'non-current liabilities': 'Non-Current Liabilities',
            'long term liabilities': 'Non-Current Liabilities',
            'long-term liabilities': 'Non-Current Liabilities',
            'long term debt': 'Non-Current Liabilities',
            
            'equity': 'Equity',
            'stockholders equity': 'Equity',
            'shareholders equity': 'Equity',
            'stockholder equity': 'Equity',
            'shareholder equity': 'Equity',
            'owners equity': 'Equity',
            'capital': 'Equity'
        }
        
        return category_map.get(category_lower, category)
    
    def normalize_amounts(self, df: pd.DataFrame, format_info: Dict) -> pd.DataFrame:
        """Normalize amount columns to consistent format"""
        
        df_processed = df.copy()
        
        for col in format_info['amount_columns']:
            if col in df_processed.columns:
                # Clean and convert amounts
                df_processed[col] = self._clean_amount_column(df_processed[col])
        
        return df_processed
    
    def _clean_amount_column(self, series: pd.Series) -> pd.Series:
        """Clean and normalize amount column"""
        
        # Convert to string first
        cleaned = series.astype(str)
        
        # Remove common formatting
        cleaned = cleaned.str.replace(',', '')
        cleaned = cleaned.str.replace('$', '')
        cleaned = cleaned.str.replace('€', '')
        cleaned = cleaned.str.replace('£', '')
        cleaned = cleaned.str.replace('₹', '')
        cleaned = cleaned.str.replace('¥', '')
        cleaned = cleaned.str.replace(' ', '')
        cleaned = cleaned.str.replace('(', '-')
        cleaned = cleaned.str.replace(')', '')
        
        # Handle parentheses as negative (accounting format)
        mask_parentheses = series.astype(str).str.contains(r'\(.*\)', na=False)
        
        # Convert to numeric
        numeric_series = pd.to_numeric(cleaned, errors='coerce')
        
        # Apply negative for parentheses format
        numeric_series[mask_parentheses] = -numeric_series[mask_parentheses].abs()
        
        return numeric_series.fillna(0)
    
    def create_standard_format(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Convert any balance sheet format to standard format"""
        
        # Step 1: Detect format
        format_info = self.detect_balance_sheet_format(df)
        
        # Step 2: Intelligent categorization
        df_categorized = self.intelligent_categorization(df, format_info)
        
        # Step 3: Normalize amounts
        df_normalized = self.normalize_amounts(df_categorized, format_info)
        
        # Step 4: Create standard format
        standard_df = self._create_standard_structure(df_normalized, format_info)
        
        return standard_df, format_info
    
    def _create_standard_structure(self, df: pd.DataFrame, format_info: Dict) -> pd.DataFrame:
        """Create standardized balance sheet structure"""
        
        account_col = format_info['account_column']
        category_col = format_info['category_column']
        amount_cols = format_info['amount_columns']
        
        if not account_col or not amount_cols:
            return df
        
        # Filter out total rows and unknown categories
        standard_df = df[
            (~df[account_col].str.contains('total', case=False, na=False)) &
            (df[category_col] != 'Unknown') if category_col else True
        ].copy()
        
        # Rename columns to standard format
        column_mapping = {account_col: 'Account'}
        if category_col:
            column_mapping[category_col] = 'Category'
        
        # Rename amount columns to standard format
        for i, col in enumerate(amount_cols):
            if '202' in col or '201' in col or '200' in col:
                # Extract year from column name
                year_match = re.search(r'(20\d{2})', col)
                if year_match:
                    column_mapping[col] = f'Amount_{year_match.group(1)}'
                else:
                    column_mapping[col] = f'Amount_Year_{i+1}'
            else:
                column_mapping[col] = f'Amount_Year_{i+1}'
        
        standard_df = standard_df.rename(columns=column_mapping)
        
        # Select only standard columns
        standard_columns = ['Account', 'Category'] + [col for col in standard_df.columns if col.startswith('Amount_')]
        
        return standard_df[standard_columns]
