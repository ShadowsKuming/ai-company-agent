import yfinance as yf
import requests
import pandas as pd
from typing import Dict, Any
import json


class CashFlowAnalyzer:
    """Analyzes company cash flow focusing on revenue streams and R&D investment"""
    
    def __init__(self):
        pass
    
    def get_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive financial data for a company"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get financial statements
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            # Get basic info
            info = stock.info
            
            return {
                'income_statement': income_stmt.to_dict() if not income_stmt.empty else {},
                'balance_sheet': balance_sheet.to_dict() if not balance_sheet.empty else {},
                'cash_flow': cash_flow.to_dict() if not cash_flow.empty else {},
                'company_info': info,
                'ticker': ticker
            }
        except Exception as e:
            return {'error': f"Failed to fetch financial data: {str(e)}"}
    
    def analyze_revenue_streams(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how the company makes money"""
        try:
            income_stmt = financial_data.get('income_statement', {})
            company_info = financial_data.get('company_info', {})
            
            # Extract revenue data
            revenue_analysis = {
                'total_revenue': {},
                'revenue_growth': {},
                'revenue_sources': [],
                'business_model': company_info.get('longBusinessSummary', 'N/A'),
                'sector': company_info.get('sector', 'N/A'),
                'industry': company_info.get('industry', 'N/A')
            }
            
            # Calculate revenue metrics
            if 'Total Revenue' in income_stmt:
                revenue_data = income_stmt['Total Revenue']
                revenue_analysis['total_revenue'] = {
                    str(date): value for date, value in revenue_data.items()
                }
                
                # Calculate growth rates
                revenue_values = list(revenue_data.values())
                if len(revenue_values) >= 2:
                    recent_growth = (revenue_values[0] - revenue_values[1]) / revenue_values[1] * 100
                    revenue_analysis['revenue_growth']['yoy_growth'] = recent_growth
            
            return revenue_analysis
            
        except Exception as e:
            return {'error': f"Failed to analyze revenue streams: {str(e)}"}
    
    def calculate_rd_ratio(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate R&D investment ratio and trends"""
        try:
            income_stmt = financial_data.get('income_statement', {})
            cash_flow = financial_data.get('cash_flow', {})
            
            rd_analysis = {
                'rd_expenses': {},
                'rd_ratio_to_revenue': {},
                'rd_trends': {},
                'future_focus_score': 0
            }
            
            # Get R&D expenses
            rd_keys = ['Research And Development', 'Research Development', 'R&D Expenses']
            revenue_keys = ['Total Revenue', 'Revenue']
            
            rd_data = None
            revenue_data = None
            
            for key in rd_keys:
                if key in income_stmt:
                    rd_data = income_stmt[key]
                    break
            
            for key in revenue_keys:
                if key in income_stmt:
                    revenue_data = income_stmt[key]
                    break
            
            if rd_data is not None and revenue_data is not None:
                # Calculate R&D ratios
                for date in rd_data.index:
                    if date in revenue_data.index and revenue_data[date] != 0:
                        rd_expense = rd_data[date]
                        revenue = revenue_data[date]
                        ratio = (rd_expense / revenue) * 100
                        
                        rd_analysis['rd_expenses'][str(date)] = rd_expense
                        rd_analysis['rd_ratio_to_revenue'][str(date)] = ratio
                
                # Calculate trend and future focus score
                ratios = list(rd_analysis['rd_ratio_to_revenue'].values())
                if len(ratios) >= 2:
                    trend = ratios[0] - ratios[-1]  # Recent vs oldest
                    rd_analysis['rd_trends']['trend_direction'] = 'increasing' if trend > 0 else 'decreasing'
                    rd_analysis['rd_trends']['trend_magnitude'] = abs(trend)
                    
                    # Future focus score (higher R&D ratio = more future focused)
                    avg_ratio = sum(ratios) / len(ratios)
                    if avg_ratio > 15:
                        rd_analysis['future_focus_score'] = 9
                    elif avg_ratio > 10:
                        rd_analysis['future_focus_score'] = 7
                    elif avg_ratio > 5:
                        rd_analysis['future_focus_score'] = 5
                    else:
                        rd_analysis['future_focus_score'] = 3
            
            return rd_analysis
            
        except Exception as e:
            return {'error': f"Failed to calculate R&D ratio: {str(e)}"}
    
    def analyze_cash_flow(self, ticker: str) -> Dict[str, Any]:
        """Complete cash flow analysis combining revenue streams and R&D investment"""
        financial_data = self.get_financial_data(ticker)
        
        if 'error' in financial_data:
            return financial_data
        
        revenue_analysis = self.analyze_revenue_streams(financial_data)
        rd_analysis = self.calculate_rd_ratio(financial_data)
        
        return {
            'ticker': ticker,
            'revenue_analysis': revenue_analysis,
            'rd_analysis': rd_analysis,
            'analysis_summary': {
                'company_name': financial_data.get('company_info', {}).get('longName', ticker),
                'sector': financial_data.get('company_info', {}).get('sector', 'N/A'),
                'market_cap': financial_data.get('company_info', {}).get('marketCap', 'N/A'),
                'future_focus_score': rd_analysis.get('future_focus_score', 0),
                'analysis_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }


class ProfitAnalyzer:
    """Analyzes how the company generates and maintains profitability"""
    
    def __init__(self):
        pass
    
    def analyze_profit_mechanisms(self, ticker: str) -> Dict[str, Any]:
        """Analyze profit margins, efficiency, and sustainability"""
        try:
            stock = yf.Ticker(ticker)
            financials = stock.financials
            info = stock.info
            
            profit_analysis = {
                'profit_margins': {},
                'profitability_trends': {},
                'efficiency_metrics': {},
                'competitive_advantages': []
            }
            
            # Calculate profit margins
            if not financials.empty:
                revenue = financials.loc['Total Revenue'] if 'Total Revenue' in financials.index else None
                gross_profit = financials.loc['Gross Profit'] if 'Gross Profit' in financials.index else None
                operating_income = financials.loc['Operating Income'] if 'Operating Income' in financials.index else None
                net_income = financials.loc['Net Income'] if 'Net Income' in financials.index else None
                
                if revenue is not None:
                    for date in revenue.index:
                        rev_val = revenue[date]
                        if rev_val != 0:
                            margins = {}
                            
                            if gross_profit is not None and date in gross_profit.index:
                                margins['gross_margin'] = (gross_profit[date] / rev_val) * 100
                            
                            if operating_income is not None and date in operating_income.index:
                                margins['operating_margin'] = (operating_income[date] / rev_val) * 100
                            
                            if net_income is not None and date in net_income.index:
                                margins['net_margin'] = (net_income[date] / rev_val) * 100
                            
                            profit_analysis['profit_margins'][str(date)] = margins
            
            # Add company-specific metrics
            profit_analysis['company_metrics'] = {
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'profit_margins_current': {
                    'gross_margin': info.get('grossMargins'),
                    'operating_margin': info.get('operatingMargins'),
                    'profit_margin': info.get('profitMargins')
                }
            }
            
            return profit_analysis
            
        except Exception as e:
            return {'error': f"Failed to analyze profit mechanisms: {str(e)}"}