import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


class ReportGenerator:
    """Generates comprehensive reports and saves them in ticker-specific folders"""
    
    def __init__(self, base_reports_dir: str = "reports"):
        self.base_reports_dir = Path(base_reports_dir)
        self.base_reports_dir.mkdir(exist_ok=True)
    
    def create_ticker_folder(self, ticker: str, analysis_date: str = None) -> Path:
        """Create date-based folder structure for ticker reports"""
        if analysis_date is None:
            analysis_date = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        
        ticker_folder = self.base_reports_dir / ticker.upper()
        ticker_folder.mkdir(exist_ok=True)
        
        # Create date-based subfolder
        analysis_folder = ticker_folder / analysis_date
        analysis_folder.mkdir(exist_ok=True)
        
        # Create subfolders within the analysis folder
        (analysis_folder / "charts").mkdir(exist_ok=True)
        (analysis_folder / "raw_data").mkdir(exist_ok=True)
        
        return analysis_folder
    
    def check_recent_analysis(self, ticker: str, days_threshold: int = 15) -> Optional[Tuple[str, Path]]:
        """Check if there's a recent analysis within the threshold"""
        ticker_folder = self.base_reports_dir / ticker.upper()
        
        if not ticker_folder.exists():
            return None
        
        # Get all analysis folders (date-time named folders)
        analysis_folders = []
        for folder in ticker_folder.iterdir():
            if folder.is_dir() and self._is_valid_date_folder(folder.name):
                try:
                    folder_date = datetime.strptime(folder.name, "%Y-%m-%d_%H%M%S")
                    analysis_folders.append((folder_date, folder))
                except ValueError:
                    continue
        
        if not analysis_folders:
            return None
        
        # Sort by date (most recent first)
        analysis_folders.sort(key=lambda x: x[0], reverse=True)
        latest_date, latest_folder = analysis_folders[0]
        
        # Check if within threshold
        days_old = (datetime.now() - latest_date).days
        if days_old <= days_threshold:
            return latest_date.strftime("%Y-%m-%d_%H%M%S"), latest_folder
        
        return None
    
    def _is_valid_date_folder(self, folder_name: str) -> bool:
        """Check if folder name matches our date format"""
        try:
            datetime.strptime(folder_name, "%Y-%m-%d_%H%M%S")
            return True
        except ValueError:
            return False
    
    def get_latest_analysis_folder(self, ticker: str) -> Optional[Path]:
        """Get the most recent analysis folder for a ticker"""
        recent_check = self.check_recent_analysis(ticker, days_threshold=365)  # Check within a year
        if recent_check:
            return recent_check[1]
        return None
    
    def save_analysis_metadata(self, analysis_folder: Path, ticker: str, analysis_summary: Dict[str, Any]) -> str:
        """Save metadata about the analysis"""
        metadata = {
            'ticker': ticker,
            'analysis_date': datetime.now().isoformat(),
            'analysis_timestamp': analysis_folder.name,
            'components_analyzed': list(analysis_summary.keys()) if analysis_summary else [],
            'analysis_duration': analysis_summary.get('analysis_duration', 'N/A'),
            'llm_used': analysis_summary.get('llm_used', 'N/A'),
            'overall_scores': analysis_summary.get('overall_scores', {}),
            'system_version': '1.0'
        }
        
        metadata_file = analysis_folder / "analysis_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return str(metadata_file)
    
    def load_recent_analysis(self, ticker: str, days_threshold: int = 15) -> Optional[Dict[str, Any]]:
        """Load recent analysis data if available"""
        recent_check = self.check_recent_analysis(ticker, days_threshold)
        if not recent_check:
            return None
        
        date_str, analysis_folder = recent_check
        
        try:
            # Load metadata
            metadata_file = analysis_folder / "analysis_metadata.json"
            if not metadata_file.exists():
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Load raw data files
            raw_data_folder = analysis_folder / "raw_data"
            analysis_data = {'metadata': metadata, 'raw_data': {}}
            
            if raw_data_folder.exists():
                for data_file in raw_data_folder.glob("*.json"):
                    try:
                        with open(data_file, 'r', encoding='utf-8') as f:
                            file_data = json.load(f)
                        analysis_data['raw_data'][data_file.stem] = file_data
                    except Exception as e:
                        print(f"Warning: Could not load {data_file}: {e}")
            
            # Add file paths
            analysis_data['analysis_folder'] = str(analysis_folder)
            analysis_data['days_old'] = (datetime.now() - datetime.fromisoformat(metadata['analysis_date'])).days
            
            return analysis_data
            
        except Exception as e:
            print(f"Error loading recent analysis: {e}")
            return None
    
    def save_raw_data(self, ticker: str, analysis_type: str, data: Dict[str, Any], analysis_folder: Path = None) -> str:
        """Save raw analysis data as JSON"""
        if analysis_folder is None:
            analysis_folder = self.create_ticker_folder(ticker)
        
        filename = f"{analysis_type}_data.json"
        filepath = analysis_folder / "raw_data" / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return str(filepath)
    
    def generate_financial_charts(self, ticker: str, financial_data: Dict[str, Any], analysis_folder: Path = None) -> Dict[str, str]:
        """Generate financial analysis charts"""
        if analysis_folder is None:
            analysis_folder = self.create_ticker_folder(ticker)
        charts_folder = analysis_folder / "charts"
        chart_files = {}
        
        try:
            # Extract data for visualization
            cash_flow_data = financial_data.get('cash_flow_analysis', {})
            profit_data = financial_data.get('profit_analysis', {})
            
            # R&D Ratio Chart
            rd_analysis = cash_flow_data.get('rd_analysis', {})
            rd_ratios = rd_analysis.get('rd_ratio_to_revenue', {})
            
            if rd_ratios:
                dates = list(rd_ratios.keys())
                ratios = list(rd_ratios.values())
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=ratios,
                    mode='lines+markers',
                    name='R&D as % of Revenue',
                    line=dict(color='blue', width=3)
                ))
                fig.update_layout(
                    title=f"{ticker} - R&D Investment Ratio Trend",
                    xaxis_title="Date",
                    yaxis_title="R&D as % of Revenue",
                    template="plotly_white"
                )
                
                chart_file = charts_folder / f"{ticker}_rd_ratio.html"
                fig.write_html(chart_file)
                chart_files['rd_ratio'] = str(chart_file)
            
            # Revenue Growth Chart
            revenue_analysis = cash_flow_data.get('revenue_analysis', {})
            total_revenue = revenue_analysis.get('total_revenue', {})
            
            if total_revenue:
                dates = list(total_revenue.keys())
                revenues = list(total_revenue.values())
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=dates,
                    y=revenues,
                    name='Total Revenue',
                    marker_color='green'
                ))
                fig.update_layout(
                    title=f"{ticker} - Revenue Trend",
                    xaxis_title="Date",
                    yaxis_title="Revenue (USD)",
                    template="plotly_white"
                )
                
                chart_file = charts_folder / f"{ticker}_revenue_trend.html"
                fig.write_html(chart_file)
                chart_files['revenue_trend'] = str(chart_file)
            
            # Profit Margins Chart
            profit_margins = profit_data.get('profit_margins', {})
            if profit_margins:
                dates = []
                gross_margins = []
                operating_margins = []
                net_margins = []
                
                for date, margins in profit_margins.items():
                    dates.append(date)
                    gross_margins.append(margins.get('gross_margin', 0))
                    operating_margins.append(margins.get('operating_margin', 0))
                    net_margins.append(margins.get('net_margin', 0))
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=gross_margins, name='Gross Margin', line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=dates, y=operating_margins, name='Operating Margin', line=dict(color='orange')))
                fig.add_trace(go.Scatter(x=dates, y=net_margins, name='Net Margin', line=dict(color='red')))
                
                fig.update_layout(
                    title=f"{ticker} - Profit Margins Trend",
                    xaxis_title="Date",
                    yaxis_title="Margin %",
                    template="plotly_white"
                )
                
                chart_file = charts_folder / f"{ticker}_profit_margins.html"
                fig.write_html(chart_file)
                chart_files['profit_margins'] = str(chart_file)
            
        except Exception as e:
            print(f"Error generating financial charts: {e}")
        
        return chart_files
    
    def generate_sentiment_chart(self, ticker: str, sentiment_data: Dict[str, Any], analysis_folder: Path = None) -> str:
        """Generate sentiment analysis chart"""
        if analysis_folder is None:
            analysis_folder = self.create_ticker_folder(ticker)
        charts_folder = analysis_folder / "charts"
        
        try:
            combined_sentiment = sentiment_data.get('combined_sentiment', {})
            news_distribution = combined_sentiment.get('sentiment_breakdown', {}).get('news_distribution', {})
            twitter_distribution = combined_sentiment.get('sentiment_breakdown', {}).get('twitter_distribution', {})
            
            if news_distribution or twitter_distribution:
                fig = make_subplots(
                    rows=1, cols=2,
                    specs=[[{"type": "pie"}, {"type": "pie"}]],
                    subplot_titles=("News Sentiment", "Twitter Sentiment")
                )
                
                if news_distribution:
                    labels = list(news_distribution.keys())
                    values = list(news_distribution.values())
                    fig.add_trace(
                        go.Pie(labels=labels, values=values, name="News"),
                        row=1, col=1
                    )
                
                if twitter_distribution:
                    labels = list(twitter_distribution.keys())
                    values = list(twitter_distribution.values())
                    fig.add_trace(
                        go.Pie(labels=labels, values=values, name="Twitter"),
                        row=1, col=2
                    )
                
                fig.update_layout(
                    title_text=f"{ticker} - Sentiment Analysis Distribution",
                    template="plotly_white"
                )
                
                chart_file = charts_folder / f"{ticker}_sentiment_analysis.html"
                fig.write_html(chart_file)
                return str(chart_file)
        
        except Exception as e:
            print(f"Error generating sentiment chart: {e}")
        
        return ""
    
    def generate_technology_score_chart(self, ticker: str, tech_data: Dict[str, Any], analysis_folder: Path = None) -> str:
        """Generate technology analysis radar chart"""
        if analysis_folder is None:
            analysis_folder = self.create_ticker_folder(ticker)
        charts_folder = analysis_folder / "charts"
        
        try:
            tech_scores = tech_data.get('technology_scores', {})
            
            if tech_scores:
                categories = ['Innovation', 'Patent Strength', 'Tech Adoption', 'Competitive Moat']
                values = [
                    tech_scores.get('innovation_score', 0),
                    tech_scores.get('patent_strength', 0),
                    tech_scores.get('tech_adoption', 0),
                    tech_scores.get('competitive_moat', 0)
                ]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=f'{ticker} Technology Score'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 10]
                        )),
                    title=f"{ticker} - Technology Analysis Radar Chart",
                    template="plotly_white"
                )
                
                chart_file = charts_folder / f"{ticker}_technology_radar.html"
                fig.write_html(chart_file)
                return str(chart_file)
        
        except Exception as e:
            print(f"Error generating technology chart: {e}")
        
        return ""
    
    def generate_markdown_report(self, ticker: str, complete_analysis: Dict[str, Any], analysis_folder: Path = None) -> str:
        """Generate comprehensive markdown report"""
        if analysis_folder is None:
            analysis_folder = self.create_ticker_folder(ticker)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Extract summary data
        company_name = complete_analysis.get('company_info', {}).get('company_name', ticker)
        
        cash_flow = complete_analysis.get('cash_flow_analysis', {})
        profit_analysis = complete_analysis.get('profit_analysis', {})
        ceo_analysis = complete_analysis.get('ceo_analysis', {})
        tech_analysis = complete_analysis.get('technology_analysis', {})
        sentiment_analysis = complete_analysis.get('sentiment_analysis', {})
        
        report_content = f"""# {company_name} ({ticker}) - Comprehensive Analysis Report

**Analysis Date:** {timestamp}
**Report Generated by:** AI Ticker Analyzer Agent

---

## Executive Summary

### Company Overview
- **Company Name:** {company_name}
- **Ticker:** {ticker}
- **Sector:** {complete_analysis.get('company_info', {}).get('sector', 'N/A')}
- **Industry:** {complete_analysis.get('company_info', {}).get('industry', 'N/A')}

### Key Metrics Summary
- **Future Focus Score (R&D):** {cash_flow.get('analysis_summary', {}).get('future_focus_score', 'N/A')}/10
- **CEO Leadership Impact:** {ceo_analysis.get('analysis_summary', {}).get('future_impact_score', 'N/A')}/10
- **Technology Score:** {tech_analysis.get('analysis_summary', {}).get('overall_tech_score', 'N/A')}/10
- **Sentiment Score:** {sentiment_analysis.get('analysis_summary', {}).get('overall_sentiment_score', 'N/A')}
- **Sentiment Category:** {sentiment_analysis.get('analysis_summary', {}).get('sentiment_category', 'N/A')}

---

## 1. Cash Flow Analysis

### Revenue Streams
{self._format_revenue_analysis(cash_flow.get('revenue_analysis', {}))}

### R&D Investment Analysis
{self._format_rd_analysis(cash_flow.get('rd_analysis', {}))}

---

## 2. Profit Mechanism Analysis

### Profitability Metrics
{self._format_profit_analysis(profit_analysis)}

---

## 3. CEO & Leadership Analysis

### CEO Information
{self._format_ceo_analysis(ceo_analysis)}

---

## 4. Technology & Innovation Analysis

### Technology Assessment
{self._format_technology_analysis(tech_analysis)}

---

## 5. Market Sentiment Analysis

### Sentiment Overview
{self._format_sentiment_analysis(sentiment_analysis)}

---

## Investment Implications

### Strengths
{self._format_strengths(complete_analysis)}

### Risks & Considerations
{self._format_risks(complete_analysis)}

---

## Data Sources & Methodology

This analysis was generated using multiple data sources including:
- Yahoo Finance for financial data
- Web scraping for CEO and leadership information
- News sources and Twitter for sentiment analysis
- Patent databases and technology news for innovation assessment

**Disclaimer:** This analysis is for informational purposes only and should not be considered as investment advice.

---

*Report generated by AI Ticker Analyzer Agent*
*Timestamp: {timestamp}*
"""
        
        report_file = analysis_folder / f"{ticker}_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_file)
    
    def _format_revenue_analysis(self, revenue_data: Dict[str, Any]) -> str:
        """Format revenue analysis section"""
        if not revenue_data:
            return "No revenue data available."
        
        business_model = revenue_data.get('business_model', 'N/A')
        sector = revenue_data.get('sector', 'N/A')
        growth = revenue_data.get('revenue_growth', {}).get('yoy_growth', 'N/A')
        
        return f"""
**Business Model:** {business_model[:300]}...

**Sector:** {sector}

**Recent Revenue Growth:** {growth}% (Year-over-Year)

**Revenue Trend:** Analysis shows the company's revenue patterns and growth trajectory.
"""
    
    def _format_rd_analysis(self, rd_data: Dict[str, Any]) -> str:
        """Format R&D analysis section"""
        if not rd_data:
            return "No R&D data available."
        
        future_score = rd_data.get('future_focus_score', 'N/A')
        trend = rd_data.get('rd_trends', {}).get('trend_direction', 'N/A')
        
        return f"""
**Future Focus Score:** {future_score}/10

**R&D Investment Trend:** {trend}

**Analysis:** The company's R&D investment ratio indicates their commitment to future innovation and technology development.
"""
    
    def _format_profit_analysis(self, profit_data: Dict[str, Any]) -> str:
        """Format profit analysis section"""
        if not profit_data:
            return "No profit analysis data available."
        
        current_margins = profit_data.get('company_metrics', {}).get('profit_margins_current', {})
        roe = profit_data.get('company_metrics', {}).get('roe', 'N/A')
        
        return f"""
**Current Profit Margins:**
- Gross Margin: {current_margins.get('gross_margin', 'N/A')}
- Operating Margin: {current_margins.get('operating_margin', 'N/A')}
- Net Margin: {current_margins.get('profit_margin', 'N/A')}

**Return on Equity (ROE):** {roe}

**Analysis:** Profit margins indicate the company's operational efficiency and pricing power.
"""
    
    def _format_ceo_analysis(self, ceo_data: Dict[str, Any]) -> str:
        """Format CEO analysis section"""
        if not ceo_data:
            return "No CEO analysis data available."
        
        summary = ceo_data.get('analysis_summary', {})
        ceo_name = summary.get('ceo_name', 'N/A')
        impact_score = summary.get('future_impact_score', 'N/A')
        strengths = summary.get('key_strengths', [])
        risks = summary.get('potential_risks', [])
        
        return f"""
**CEO:** {ceo_name}

**Leadership Impact Score:** {impact_score}/10

**Key Strengths:**
{chr(10).join(f"- {strength}" for strength in strengths)}

**Potential Risks:**
{chr(10).join(f"- {risk}" for risk in risks)}
"""
    
    def _format_technology_analysis(self, tech_data: Dict[str, Any]) -> str:
        """Format technology analysis section"""
        if not tech_data:
            return "No technology analysis data available."
        
        summary = tech_data.get('analysis_summary', {})
        tech_score = summary.get('overall_tech_score', 'N/A')
        strengths = summary.get('key_strengths', [])
        risks = summary.get('potential_risks', [])
        focus_areas = summary.get('technology_focus_areas', [])
        
        return f"""
**Technology Score:** {tech_score}/10

**Technology Focus Areas:** {', '.join(focus_areas)}

**Technology Strengths:**
{chr(10).join(f"- {strength}" for strength in strengths)}

**Technology Risks:**
{chr(10).join(f"- {risk}" for risk in risks)}
"""
    
    def _format_sentiment_analysis(self, sentiment_data: Dict[str, Any]) -> str:
        """Format sentiment analysis section"""
        if not sentiment_data:
            return "No sentiment analysis data available."
        
        summary = sentiment_data.get('analysis_summary', {})
        sentiment_score = summary.get('overall_sentiment_score', 'N/A')
        sentiment_category = summary.get('sentiment_category', 'N/A')
        confidence = summary.get('confidence_level', 'N/A')
        data_quality = summary.get('data_quality', {})
        
        return f"""
**Overall Sentiment Score:** {sentiment_score}

**Sentiment Category:** {sentiment_category.title()}

**Confidence Level:** {confidence}

**Data Sources:**
- News Articles Analyzed: {data_quality.get('news_articles_analyzed', 'N/A')}
- Tweets Analyzed: {data_quality.get('tweets_analyzed', 'N/A')}
"""
    
    def _format_strengths(self, complete_analysis: Dict[str, Any]) -> str:
        """Format overall strengths"""
        strengths = []
        
        # Collect strengths from each analysis
        for analysis_type in ['ceo_analysis', 'technology_analysis']:
            if analysis_type in complete_analysis:
                analysis_strengths = complete_analysis[analysis_type].get('analysis_summary', {}).get('key_strengths', [])
                strengths.extend(analysis_strengths)
        
        return chr(10).join(f"- {strength}" for strength in strengths[:5])  # Top 5 strengths
    
    def _format_risks(self, complete_analysis: Dict[str, Any]) -> str:
        """Format overall risks"""
        risks = []
        
        # Collect risks from each analysis
        for analysis_type in ['ceo_analysis', 'technology_analysis']:
            if analysis_type in complete_analysis:
                analysis_risks = complete_analysis[analysis_type].get('analysis_summary', {}).get('potential_risks', [])
                risks.extend(analysis_risks)
        
        return chr(10).join(f"- {risk}" for risk in risks[:5])  # Top 5 risks
    
    def generate_complete_report(self, ticker: str, complete_analysis: Dict[str, Any], analysis_folder: Path = None) -> Dict[str, str]:
        """Generate complete report with all components"""
        try:
            # Create or use provided analysis folder
            if analysis_folder is None:
                analysis_folder = self.create_ticker_folder(ticker)
            
            # Save raw data
            raw_data_files = {}
            for analysis_type, data in complete_analysis.items():
                if isinstance(data, dict) and data:
                    raw_data_files[analysis_type] = self.save_raw_data(ticker, analysis_type, data, analysis_folder)
            
            # Generate charts
            chart_files = {}
            if 'cash_flow_analysis' in complete_analysis or 'profit_analysis' in complete_analysis:
                financial_charts = self.generate_financial_charts(ticker, complete_analysis, analysis_folder)
                chart_files.update(financial_charts)
            
            if 'sentiment_analysis' in complete_analysis:
                sentiment_chart = self.generate_sentiment_chart(ticker, complete_analysis['sentiment_analysis'], analysis_folder)
                if sentiment_chart:
                    chart_files['sentiment_chart'] = sentiment_chart
            
            if 'technology_analysis' in complete_analysis:
                tech_chart = self.generate_technology_score_chart(ticker, complete_analysis['technology_analysis'], analysis_folder)
                if tech_chart:
                    chart_files['technology_chart'] = tech_chart
            
            # Generate markdown report
            report_file = self.generate_markdown_report(ticker, complete_analysis, analysis_folder)
            
            # Save analysis metadata
            analysis_summary = complete_analysis.get('analysis_summary', {})
            metadata_file = self.save_analysis_metadata(analysis_folder, ticker, analysis_summary)
            
            return {
                'report_file': report_file,
                'raw_data_files': raw_data_files,
                'chart_files': chart_files,
                'metadata_file': metadata_file,
                'analysis_folder': str(analysis_folder)
            }
            
        except Exception as e:
            return {'error': f"Failed to generate complete report: {str(e)}"}