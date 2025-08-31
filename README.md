# AI-Powered Balance Sheet Summary Generator

A Streamlit web application that provides automated balance sheet analysis and summaries using AI-powered insights.

## Features

- 📊 Interactive balance sheet data visualization
- 🧠 AI-powered financial analysis and insights
- 📈 Key financial ratios calculation (Current Ratio, Debt-to-Equity, etc.)
- 📋 Year-over-year comparison analysis
- 💡 Automated insight generation
- 📄 Executive summary reports
- 📥 Downloadable analysis reports

## Key Capabilities

- **Liquidity Analysis**: Current ratio analysis and trends
- **Leverage Analysis**: Debt-to-equity ratio evaluation
- **Asset Composition**: Breakdown of current vs non-current assets
- **Trend Analysis**: Year-over-year performance comparison
- **Visual Dashboard**: Interactive charts and graphs
- **Executive Summary**: AI-generated business insights

## Technology Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly
- **AI Analysis**: Custom algorithms for financial analysis

## Project Structure

```
balance sheet summary/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── .env.example          # Environment variables template
```

## Sample Data

The application comes with built-in sample data that includes:
- Current and non-current assets
- Current and long-term liabilities  
- Equity components
- Multi-year comparison data

## Analysis Features

### Financial Ratios
- **Current Ratio**: Measures liquidity (Current Assets / Current Liabilities)
- **Debt-to-Equity Ratio**: Measures leverage (Total Liabilities / Total Equity)
- **Asset Composition**: Percentage breakdown of asset types

### AI Insights
- Liquidity position assessment
- Leverage risk evaluation
- Asset structure analysis
- Trend identification
- Performance recommendations

### Visualizations
1. **Balance Sheet Composition**: Pie chart showing asset/liability/equity breakdown
2. **Year-over-Year Comparison**: Bar chart comparing categories across years
3. **Key Ratios Trend**: Line chart showing financial ratios over time

## Usage

1. Launch the application
2. Choose to use sample data or upload your own Excel/CSV file
3. View the interactive dashboard with key metrics
4. Analyze AI-generated insights
5. Download detailed reports

## Data Format

For custom data upload, use this format:

| Account | Category | Amount_2023 | Amount_2022 |
|---------|----------|-------------|-------------|
| Cash | Current Assets | 850000 | 750000 |
| Accounts Payable | Current Liabilities | -280000 | -260000 |

**Note**: Use negative values for liabilities and equity accounts.

## Future Enhancements

- Integration with accounting software APIs
- More advanced AI models for deeper insights
- Industry benchmarking capabilities
- Multi-company comparison features
- Automated report scheduling
