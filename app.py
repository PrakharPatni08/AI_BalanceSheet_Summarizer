import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
from typing import Dict, List, Tuple
import re
from intelligent_parser import IntelligentBalanceSheetParser

# Gemini integration
from gemini_client import GeminiClient

class BalanceSheetAnalyzer:
    """AI-powered Balance Sheet Analyzer with Intelligent Parsing"""
    
    def __init__(self):
        self.balance_sheet_data = None
        self.analysis_results = {}
        self.parser = IntelligentBalanceSheetParser()
        
    def process_any_balance_sheet(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Process any balance sheet format and convert to standard format"""
        try:
            standard_df, format_info = self.parser.create_standard_format(df)
            return standard_df, format_info
        except Exception as e:
            st.error(f"Error processing balance sheet: {str(e)}")
            return df, {}
        
    def load_sample_data(self) -> pd.DataFrame:
        """Generate sample balance sheet data"""
        sample_data = {
            'Account': [
                # Assets
                'Cash and Cash Equivalents',
                'Accounts Receivable',
                'Inventory',
                'Prepaid Expenses',
                'Property, Plant & Equipment',
                'Intangible Assets',
                'Investments',
                # Liabilities
                'Accounts Payable',
                'Short-term Debt',
                'Accrued Liabilities',
                'Long-term Debt',
                'Deferred Tax Liabilities',
                # Equity
                'Common Stock',
                'Retained Earnings',
                'Additional Paid-in Capital'
            ],
            'Category': [
                'Current Assets', 'Current Assets', 'Current Assets', 'Current Assets',
                'Non-Current Assets', 'Non-Current Assets', 'Non-Current Assets',
                'Current Liabilities', 'Current Liabilities', 'Current Liabilities',
                'Non-Current Liabilities', 'Non-Current Liabilities',
                'Equity', 'Equity', 'Equity'
            ],
            'Amount_2023': [
                850000, 420000, 320000, 45000,
                1200000, 180000, 250000,
                -280000, -150000, -95000,
                -650000, -85000,
                -500000, -1200000, -305000
            ],
            'Amount_2022': [
                750000, 380000, 290000, 38000,
                1100000, 165000, 220000,
                -260000, -180000, -87000,
                -720000, -75000,
                -500000, -950000, -266000
            ]
        }
        return pd.DataFrame(sample_data)
    
    def analyze_balance_sheet(self, df: pd.DataFrame) -> Dict:
        """Perform comprehensive balance sheet analysis"""
        
        # Calculate totals for each category
        current_year = df.columns[-2]  # Assuming last column is most recent
        previous_year = df.columns[-1]
        
        analysis = {
            'current_year': current_year,
            'previous_year': previous_year,
            'ratios': {},
            'trends': {},
            'insights': []
        }
        
        # Calculate key metrics for both years
        for year_col in [current_year, previous_year]:
            year_data = df.groupby('Category')[year_col].sum()
            
            current_assets = abs(year_data.get('Current Assets', 0))
            non_current_assets = abs(year_data.get('Non-Current Assets', 0))
            current_liabilities = abs(year_data.get('Current Liabilities', 0))
            non_current_liabilities = abs(year_data.get('Non-Current Liabilities', 0))
            equity = abs(year_data.get('Equity', 0))
            
            total_assets = current_assets + non_current_assets
            total_liabilities = current_liabilities + non_current_liabilities
            
            year_key = year_col.split('_')[1] if '_' in year_col else year_col
            
            analysis['ratios'][year_key] = {
                'current_ratio': current_assets / current_liabilities if current_liabilities > 0 else 0,
                'debt_to_equity': total_liabilities / equity if equity > 0 else 0,
                'asset_composition': {
                    'current_assets_pct': (current_assets / total_assets * 100) if total_assets > 0 else 0,
                    'non_current_assets_pct': (non_current_assets / total_assets * 100) if total_assets > 0 else 0
                },
                'totals': {
                    'total_assets': total_assets,
                    'total_liabilities': total_liabilities,
                    'total_equity': equity
                }
            }
        
        # Calculate trends
        if len(analysis['ratios']) >= 2:
            years = sorted(analysis['ratios'].keys())
            current_year_key, previous_year_key = years[-1], years[-2]
            
            current_data = analysis['ratios'][current_year_key]
            previous_data = analysis['ratios'][previous_year_key]
            
            analysis['trends'] = {
                'current_ratio_change': current_data['current_ratio'] - previous_data['current_ratio'],
                'debt_to_equity_change': current_data['debt_to_equity'] - previous_data['debt_to_equity'],
                'total_assets_change_pct': ((current_data['totals']['total_assets'] - previous_data['totals']['total_assets']) / previous_data['totals']['total_assets'] * 100) if previous_data['totals']['total_assets'] > 0 else 0
            }
        
        return analysis
    
    def generate_ai_insights(self, analysis: Dict) -> List[str]:
        """Generate AI-powered insights based on analysis"""
        insights = []
        
        if not analysis.get('ratios'):
            return ["Unable to generate insights due to insufficient data."]
        
        # Get latest year data
        latest_year = max(analysis['ratios'].keys())
        ratios = analysis['ratios'][latest_year]
        trends = analysis.get('trends', {})
        
        # Liquidity Analysis
        current_ratio = ratios.get('current_ratio', 0)
        if current_ratio > 2:
            insights.append(f"🟢 **Strong Liquidity**: Current ratio of {current_ratio:.2f} indicates excellent ability to meet short-term obligations.")
        elif current_ratio > 1:
            insights.append(f"🟡 **Adequate Liquidity**: Current ratio of {current_ratio:.2f} shows reasonable liquidity position.")
        else:
            insights.append(f"🔴 **Liquidity Concern**: Current ratio of {current_ratio:.2f} suggests potential difficulty meeting short-term obligations.")
        
        # Leverage Analysis
        debt_to_equity = ratios.get('debt_to_equity', 0)
        if debt_to_equity < 0.5:
            insights.append(f"🟢 **Conservative Leverage**: Debt-to-equity ratio of {debt_to_equity:.2f} indicates low financial risk.")
        elif debt_to_equity < 1:
            insights.append(f"🟡 **Moderate Leverage**: Debt-to-equity ratio of {debt_to_equity:.2f} shows balanced capital structure.")
        else:
            insights.append(f"🔴 **High Leverage**: Debt-to-equity ratio of {debt_to_equity:.2f} suggests high financial risk.")
        
        # Asset Composition
        current_assets_pct = ratios.get('asset_composition', {}).get('current_assets_pct', 0)
        if current_assets_pct > 60:
            insights.append(f"📊 **Asset Structure**: {current_assets_pct:.1f}% of assets are current, indicating high liquidity focus.")
        elif current_assets_pct < 30:
            insights.append(f"📊 **Asset Structure**: {current_assets_pct:.1f}% of assets are current, showing emphasis on long-term investments.")
        
        # Trend Analysis
        if trends.get('current_ratio_change', 0) > 0.1:
            insights.append("📈 **Improving Liquidity**: Current ratio has improved significantly year-over-year.")
        elif trends.get('current_ratio_change', 0) < -0.1:
            insights.append("📉 **Declining Liquidity**: Current ratio has deteriorated year-over-year.")
        
        if trends.get('total_assets_change_pct', 0) > 10:
            insights.append(f"🚀 **Strong Growth**: Total assets increased by {trends['total_assets_change_pct']:.1f}% indicating business expansion.")
        elif trends.get('total_assets_change_pct', 0) < -5:
            insights.append(f"⚠️ **Asset Decline**: Total assets decreased by {abs(trends['total_assets_change_pct']):.1f}% requiring attention.")
        
        return insights
    
    def create_visualizations(self, df: pd.DataFrame, analysis: Dict) -> Tuple[go.Figure, go.Figure, go.Figure]:
        """Create interactive visualizations"""
        
        # 1. Balance Sheet Composition Pie Chart
        latest_year_col = df.columns[-2]
        category_totals = df.groupby('Category')[latest_year_col].sum().abs()
        
        fig1 = px.pie(
            values=category_totals.values,
            names=category_totals.index,
            title=f"Balance Sheet Composition ({latest_year_col.split('_')[-1]})",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        
        # 2. Year-over-Year Comparison
        df_melted = df.melt(
            id_vars=['Account', 'Category'],
            value_vars=[col for col in df.columns if 'Amount_' in col],
            var_name='Year',
            value_name='Amount'
        )
        df_melted['Year'] = df_melted['Year'].str.replace('Amount_', '')
        df_melted['Amount'] = df_melted['Amount'].abs()
        
        category_comparison = df_melted.groupby(['Category', 'Year'])['Amount'].sum().reset_index()
        
        fig2 = px.bar(
            category_comparison,
            x='Category',
            y='Amount',
            color='Year',
            title='Year-over-Year Category Comparison',
            barmode='group'
        )
        fig2.update_layout(xaxis_tickangle=-45)
        
        # 3. Key Ratios Dashboard
        if analysis.get('ratios') and len(analysis['ratios']) >= 2:
            years = sorted(analysis['ratios'].keys())
            metrics = ['current_ratio', 'debt_to_equity']
            
            ratio_data = []
            for year in years:
                for metric in metrics:
                    ratio_data.append({
                        'Year': year,
                        'Metric': metric.replace('_', ' ').title(),
                        'Value': analysis['ratios'][year].get(metric, 0)
                    })
            
            ratio_df = pd.DataFrame(ratio_data)
            
            fig3 = px.line(
                ratio_df,
                x='Year',
                y='Value',
                color='Metric',
                title='Key Financial Ratios Trend',
                markers=True
            )
            fig3.update_layout(yaxis_title='Ratio Value')
        else:
            # Create empty figure if insufficient data
            fig3 = go.Figure()
            fig3.add_annotation(text="Insufficient data for ratio trends", 
                              xref="paper", yref="paper",
                              x=0.5, y=0.5, showarrow=False)
            fig3.update_layout(title='Key Financial Ratios Trend')
        
        return fig1, fig2, fig3

def main():
    st.set_page_config(
        page_title="AI Balance Sheet Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    # Header
    st.title("📊 AI-Powered Balance Sheet Summary Generator")
    st.markdown("---")
    
    # Initialize analyzer
    analyzer = BalanceSheetAnalyzer()
    
    # Sidebar
    st.sidebar.header("📁 Data Input")
    data_option = st.sidebar.radio(
        "Choose data source:",
        ["Use Sample Data", "Upload Your Data"]
    )
    
    # Data loading
    if data_option == "Use Sample Data":
        df = analyzer.load_sample_data()
        st.sidebar.success("✅ Sample data loaded successfully!")
        format_info = {}
    else:
        uploaded_file = st.sidebar.file_uploader(
            "Upload Balance Sheet (Excel/CSV)",
            type=['xlsx', 'xls', 'csv'],
            help="Upload any balance sheet format - the AI will automatically detect and process it!"
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    raw_df = pd.read_csv(uploaded_file)
                else:
                    raw_df = pd.read_excel(uploaded_file)
                
                # Process the uploaded data with intelligent parsing
                with st.spinner("🧠 Analyzing balance sheet format..."):
                    df, format_info = analyzer.process_any_balance_sheet(raw_df)
                
                st.sidebar.success("✅ File uploaded and processed successfully!")
                
                # Show format detection info
                if format_info:
                    st.sidebar.info(f"🔍 Detected format: {format_info.get('format_type', 'unknown')}")
                    if format_info.get('has_categories'):
                        st.sidebar.info("📊 Categories detected automatically")
                    else:
                        st.sidebar.info("🤖 AI categorization applied")
                        
            except Exception as e:
                st.sidebar.error(f"❌ Error loading file: {str(e)}")
                df = analyzer.load_sample_data()
                format_info = {}
                st.sidebar.info("🔄 Using sample data instead")
        else:
            df = analyzer.load_sample_data()
            format_info = {}
            st.sidebar.info("🔄 Using sample data for demo")
    
    # Data preview
    if df is not None:
        # Format information display
        if format_info:
            st.subheader("� Balance Sheet Format Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Format Type", format_info.get('format_type', 'Unknown').title())
            
            with col2:
                categorization = "Auto-Detected" if format_info.get('has_categories') else "AI-Generated"
                st.metric("Categorization", categorization)
            
            with col3:
                st.metric("Amount Columns", len(format_info.get('amount_columns', [])))
            
            # Show detected structure
            if format_info.get('account_column') or format_info.get('category_column'):
                st.info(f"**Detected Structure:** Account Column: `{format_info.get('account_column', 'N/A')}`, "
                       f"Category Column: `{format_info.get('category_column', 'N/A')}`")
        
        st.subheader("�📋 Processed Balance Sheet Data")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(df, use_container_width=True)
        
        with col2:
            st.metric("Total Accounts", len(df))
            st.metric("Categories", df['Category'].nunique())
            st.metric("Years of Data", len([col for col in df.columns if 'Amount_' in col]))
        
        # Analysis
        st.subheader("🧠 AI-Powered Analysis")
        
        with st.spinner("Analyzing balance sheet..."):
            analysis = analyzer.analyze_balance_sheet(df)
            insights = analyzer.generate_ai_insights(analysis)
        
        # Display insights
        st.subheader("💡 Key Insights")
        for insight in insights:
            st.markdown(f"- {insight}")
        
        # Metrics dashboard
        if analysis.get('ratios'):
            st.subheader("📊 Key Financial Metrics")
            
            latest_year = max(analysis['ratios'].keys())
            metrics = analysis['ratios'][latest_year]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Current Ratio",
                    f"{metrics.get('current_ratio', 0):.2f}",
                    delta=f"{analysis.get('trends', {}).get('current_ratio_change', 0):.2f}" if analysis.get('trends') else None
                )
            
            with col2:
                st.metric(
                    "Debt-to-Equity",
                    f"{metrics.get('debt_to_equity', 0):.2f}",
                    delta=f"{analysis.get('trends', {}).get('debt_to_equity_change', 0):.2f}" if analysis.get('trends') else None
                )
            
            with col3:
                total_assets = metrics.get('totals', {}).get('total_assets', 0)
                st.metric(
                    "Total Assets",
                    f"${total_assets:,.0f}",
                    delta=f"{analysis.get('trends', {}).get('total_assets_change_pct', 0):.1f}%" if analysis.get('trends') else None
                )
            
            with col4:
                current_assets_pct = metrics.get('asset_composition', {}).get('current_assets_pct', 0)
                st.metric(
                    "Current Assets %",
                    f"{current_assets_pct:.1f}%"
                )
        
        # Visualizations
        st.subheader("📈 Interactive Visualizations")
        
        with st.spinner("Creating visualizations..."):
            fig1, fig2, fig3 = analyzer.create_visualizations(df, analysis)
        
        # Display charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig2, use_container_width=True)
        
        # Summary Report
        st.subheader("📄 Executive Summary")
        
        if analysis.get('ratios'):
            latest_year = max(analysis['ratios'].keys())
            metrics = analysis['ratios'][latest_year]
            # Compose prompt for Gemini
            gemini_prompt = f"""
            You are a financial analyst. Summarize the following balance sheet analysis in clear, professional language for an executive audience:
            Year: {latest_year}
            Current Ratio: {metrics.get('current_ratio', 0):.2f}
            Debt-to-Equity Ratio: {metrics.get('debt_to_equity', 0):.2f}
            Total Assets: ${metrics.get('totals', {}).get('total_assets', 0):,.0f}
            Current Assets %: {metrics.get('asset_composition', {}).get('current_assets_pct', 0):.1f}%
            Non-Current Assets %: {metrics.get('asset_composition', {}).get('non_current_assets_pct', 0):.1f}%
            Key Insights: {'; '.join(insights[:3])}
            """
            gemini_client = GeminiClient()
            with st.spinner("Generating executive summary with Gemini..."):
                gemini_summary = gemini_client.generate_summary(gemini_prompt)
            st.markdown(gemini_summary)
        
        # Download option
        if st.button("📥 Generate Detailed Report"):
            # Create a simple report
            report_data = {
                'Analysis_Date': [datetime.now().strftime('%Y-%m-%d')],
                'Current_Ratio': [analysis['ratios'][max(analysis['ratios'].keys())]['current_ratio'] if analysis.get('ratios') else 0],
                'Debt_to_Equity': [analysis['ratios'][max(analysis['ratios'].keys())]['debt_to_equity'] if analysis.get('ratios') else 0],
                'Total_Assets': [analysis['ratios'][max(analysis['ratios'].keys())]['totals']['total_assets'] if analysis.get('ratios') else 0],
                'Key_Insights': ['; '.join(insights)]
            }
            
            report_df = pd.DataFrame(report_data)
            
            # Convert to CSV for download
            csv_buffer = io.StringIO()
            report_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            st.download_button(
                label="📄 Download Analysis Report (CSV)",
                data=csv_data,
                file_name=f"balance_sheet_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with Streamlit and AI-powered analysis*")

if __name__ == "__main__":
    main()
