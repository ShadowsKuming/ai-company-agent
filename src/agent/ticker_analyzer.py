import asyncio
from typing import Dict, Any, Optional
import time
from datetime import datetime

# Import analysis tools
from src.tool.financial_analysis import CashFlowAnalyzer, ProfitAnalyzer
from src.tool.ceo_analysis import CEOAnalyzer
from src.tool.technology_analysis import TechnologyAnalyzer
from src.tool.sentiment_analysis import SentimentAnalyzer
from src.tool.report_generator import ReportGenerator

# Import LLM configuration
from src.config import default_llm, llm_type, get_gemini_model, get_openai_model


class TickerAnalyzerAgent:
    """Main agent that orchestrates comprehensive ticker analysis"""
    
    def __init__(self, use_llm: str = "gemini"):
        """Initialize the ticker analyzer agent
        
        Args:
            use_llm: "gemini" for Gemini Pro or "openai" for ChatGPT-4o
        """
        self.use_llm = use_llm
        
        # Initialize LLM based on preference
        if use_llm == "gemini":
            try:
                self.llm = get_gemini_model()
                self.llm_type = "gemini"
            except ValueError:
                self.llm = get_openai_model()
                self.llm_type = "openai"
        else:
            try:
                self.llm = get_openai_model()
                self.llm_type = "openai"
            except ValueError:
                self.llm = get_gemini_model()
                self.llm_type = "gemini"
        
        # Initialize analysis tools
        self.cash_flow_analyzer = CashFlowAnalyzer()
        self.profit_analyzer = ProfitAnalyzer()
        self.ceo_analyzer = CEOAnalyzer()
        self.technology_analyzer = TechnologyAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.report_generator = ReportGenerator()
        
        print(f"[OK] Ticker Analyzer Agent initialized with {self.llm_type.upper()} LLM")
    
    def get_llm_analysis(self, prompt: str, data: Dict[str, Any]) -> str:
        """Get analysis from LLM based on data and prompt"""
        try:
            if self.llm_type == "gemini":
                response = self.llm.generate_content(f"{prompt}\n\nData: {str(data)[:2000]}")
                return response.text
            else:  # OpenAI
                response = self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a financial analysis expert."},
                        {"role": "user", "content": f"{prompt}\n\nData: {str(data)[:2000]}"}
                    ],
                    max_tokens=500
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"LLM analysis failed: {str(e)}"
    
    def analyze_ticker_comprehensive(self, ticker: str, company_name: Optional[str] = None, force_new: bool = False) -> Dict[str, Any]:
        """Run comprehensive analysis on a ticker symbol
        
        Args:
            ticker: Stock ticker symbol
            company_name: Optional company name
            force_new: If True, skip cache and run new analysis
        """
        
        print(f"\n[ANALYZE] Starting analysis for {ticker.upper()}")
        print("=" * 60)
        
        # Check for recent analysis first (unless force_new is True)
        if not force_new:
            recent_analysis = self.report_generator.load_recent_analysis(ticker, days_threshold=15)
            if recent_analysis:
                days_old = recent_analysis['days_old']
                analysis_date = recent_analysis['metadata']['analysis_date']
                
                print(f"[CACHE] Found recent analysis from {days_old} days ago ({analysis_date})")
                print(f"[CACHE] Using cached results from: {recent_analysis['analysis_folder']}")
                print("=" * 60)
                
                # Reconstruct the analysis results from cached data
                cached_results = self._reconstruct_analysis_from_cache(recent_analysis)
                cached_results['is_cached'] = True
                cached_results['cache_age_days'] = days_old
                cached_results['original_analysis_date'] = analysis_date
                
                return cached_results
            else:
                print("[NEW] No recent analysis found. Running new comprehensive analysis...")
                print("=" * 60)
        
        start_time = time.time()
        analysis_results = {
            'ticker': ticker.upper(),
            'analysis_timestamp': datetime.now().isoformat(),
            'llm_used': self.llm_type,
            'company_info': {},
            'cash_flow_analysis': {},
            'profit_analysis': {},
            'ceo_analysis': {},
            'technology_analysis': {},
            'sentiment_analysis': {},
            'llm_insights': {},
            'overall_scores': {},
            'analysis_status': {}
        }
        
        # 0. Pre-validation: Check if ticker is valid
        print("[VALIDATION] Validating ticker and basic data availability...")
        try:
            test_financial_data = self.cash_flow_analyzer.get_financial_data(ticker)
            if 'error' in test_financial_data:
                print(f"   [CRITICAL] {test_financial_data['error']}")
                print(f"   [STOP] Cannot proceed with analysis - invalid ticker or no data available")
                return {
                    'ticker': ticker.upper(),
                    'error': test_financial_data['error'],
                    'analysis_timestamp': datetime.now().isoformat(),
                    'analysis_status': 'failed_validation'
                }
            print(f"   [OK] Ticker validation successful")
        except Exception as e:
            error_msg = f"Ticker validation failed: {str(e)}"
            print(f"   [CRITICAL] {error_msg}")
            return {
                'ticker': ticker.upper(),
                'error': error_msg,
                'analysis_timestamp': datetime.now().isoformat(),
                'analysis_status': 'failed_validation'
            }
        
        # 1. Cash Flow Analysis
        print("[CASH_FLOW] Running cash flow analysis...")
        try:
            cash_flow_result = self.cash_flow_analyzer.analyze_cash_flow(ticker)
            
            # Check if cash flow analysis failed
            if 'error' in cash_flow_result:
                print(f"   [FAIL] Cash flow analysis failed: {cash_flow_result['error']}")
                analysis_results['analysis_status']['cash_flow'] = f"failed: {cash_flow_result['error']}"
                # Don't return early here since other analyses might still work
            else:
                analysis_results['cash_flow_analysis'] = cash_flow_result
                analysis_results['analysis_status']['cash_flow'] = 'completed'
                
                if 'analysis_summary' in cash_flow_result:
                    analysis_results['company_info'].update(cash_flow_result['analysis_summary'])
                
                print(f"   [OK] Cash flow analysis completed")
            
        except Exception as e:
            print(f"   [FAIL] Cash flow analysis failed: {e}")
            analysis_results['analysis_status']['cash_flow'] = f'failed: {e}'
        
        # 2. Profit Analysis
        print("[PROFIT] Running profit mechanism analysis...")
        try:
            profit_result = self.profit_analyzer.analyze_profit_mechanisms(ticker)
            analysis_results['profit_analysis'] = profit_result
            analysis_results['analysis_status']['profit'] = 'completed'
            print(f"   [OK] Profit analysis completed")
            
        except Exception as e:
            print(f"   [FAIL] Profit analysis failed: {e}")
            analysis_results['analysis_status']['profit'] = f'failed: {e}'
        
        # 3. CEO Analysis
        print("[CEO] Running CEO & leadership analysis...")
        try:
            ceo_result = self.ceo_analyzer.analyze_ceo_complete(ticker)
            analysis_results['ceo_analysis'] = ceo_result
            analysis_results['analysis_status']['ceo'] = 'completed'
            print(f"   [OK] CEO analysis completed")
            
        except Exception as e:
            print(f"   [FAIL] CEO analysis failed: {e}")
            analysis_results['analysis_status']['ceo'] = f'failed: {e}'
        
        # 4. Technology Analysis
        print("[TECH] Running technology & IP analysis...")
        try:
            tech_result = self.technology_analyzer.analyze_technology_complete(ticker)
            analysis_results['technology_analysis'] = tech_result
            analysis_results['analysis_status']['technology'] = 'completed'
            print(f"   [OK] Technology analysis completed")
            
        except Exception as e:
            print(f"   [FAIL] Technology analysis failed: {e}")
            analysis_results['analysis_status']['technology'] = f'failed: {e}'
        
        # 5. Sentiment Analysis
        print("[SENTIMENT] Running market sentiment analysis...")
        try:
            sentiment_result = self.sentiment_analyzer.analyze_sentiment_complete(ticker)
            analysis_results['sentiment_analysis'] = sentiment_result
            analysis_results['analysis_status']['sentiment'] = 'completed'
            print(f"   [OK] Sentiment analysis completed")
            
        except Exception as e:
            print(f"   [FAIL] Sentiment analysis failed: {e}")
            analysis_results['analysis_status']['sentiment'] = f'failed: {e}'
        
        # 6. Generate LLM Insights
        print("[AI] Generating AI insights...")
        try:
            insights = self.generate_llm_insights(analysis_results)
            analysis_results['llm_insights'] = insights
            print(f"   [OK] AI insights generated")
            
        except Exception as e:
            print(f"   [FAIL] AI insights generation failed: {e}")
            analysis_results['llm_insights'] = {'error': str(e)}
        
        # 7. Calculate Overall Scores
        analysis_results['overall_scores'] = self.calculate_overall_scores(analysis_results)
        
        # 8. Generate Reports
        print("[REPORT] Generating comprehensive report...")
        try:
            report_result = self.report_generator.generate_complete_report(ticker, analysis_results)
            analysis_results['report_files'] = report_result
            print(f"   [OK] Report generated: {report_result.get('report_file', 'N/A')}")
            
        except Exception as e:
            print(f"   [FAIL] Report generation failed: {e}")
            analysis_results['report_files'] = {'error': str(e)}
        
        # Analysis summary
        total_time = time.time() - start_time
        analysis_results['analysis_duration'] = f"{total_time:.2f} seconds"
        
        print("\n" + "=" * 60)
        print(f"🎯 Analysis completed in {total_time:.2f} seconds")
        print(f"📁 Results saved in: reports/{ticker.upper()}/")
        
        return analysis_results
    
    def generate_llm_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate AI-powered insights from the analysis results"""
        insights = {}
        
        # Financial insights
        if analysis_results.get('cash_flow_analysis') and analysis_results.get('profit_analysis'):
            financial_prompt = """
            Based on the cash flow and profit analysis data, provide a concise insight about:
            1. The company's financial health and sustainability
            2. Revenue growth potential and R&D investment effectiveness
            3. Key financial strengths and risks for future performance
            Keep it under 200 words.
            """
            financial_data = {
                'cash_flow': analysis_results['cash_flow_analysis'],
                'profit': analysis_results['profit_analysis']
            }
            insights['financial_insight'] = self.get_llm_analysis(financial_prompt, financial_data)
        
        # Leadership insights
        if analysis_results.get('ceo_analysis'):
            leadership_prompt = """
            Based on the CEO and leadership analysis, provide insights about:
            1. How the leadership might impact the company's future
            2. Key leadership strengths and potential concerns
            3. Leadership's alignment with future market trends
            Keep it under 150 words.
            """
            insights['leadership_insight'] = self.get_llm_analysis(leadership_prompt, analysis_results['ceo_analysis'])
        
        # Technology insights
        if analysis_results.get('technology_analysis'):
            tech_prompt = """
            Based on the technology and IP analysis, provide insights about:
            1. The company's technological competitive position
            2. Innovation capacity and patent strength
            3. Technology risks and opportunities for the future
            Keep it under 150 words.
            """
            insights['technology_insight'] = self.get_llm_analysis(tech_prompt, analysis_results['technology_analysis'])
        
        # Market sentiment insights
        if analysis_results.get('sentiment_analysis'):
            sentiment_prompt = """
            Based on the sentiment analysis, provide insights about:
            1. Current market perception and confidence
            2. Potential impact of sentiment on stock performance
            3. Key themes driving positive or negative sentiment
            Keep it under 150 words.
            """
            insights['sentiment_insight'] = self.get_llm_analysis(sentiment_prompt, analysis_results['sentiment_analysis'])
        
        return insights
    
    def calculate_overall_scores(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall scores and ratings"""
        scores = {
            'future_focus_score': 0,
            'leadership_score': 0,
            'technology_score': 0,
            'financial_health_score': 0,
            'sentiment_score': 0,
            'overall_investment_score': 0,
            'risk_level': 'medium'
        }
        
        # Extract individual scores
        cash_flow = analysis_results.get('cash_flow_analysis', {})
        ceo_analysis = analysis_results.get('ceo_analysis', {})
        tech_analysis = analysis_results.get('technology_analysis', {})
        sentiment_analysis = analysis_results.get('sentiment_analysis', {})
        
        # Future focus (R&D investment)
        if 'analysis_summary' in cash_flow:
            scores['future_focus_score'] = cash_flow['analysis_summary'].get('future_focus_score', 0)
        
        # Leadership score
        if 'analysis_summary' in ceo_analysis:
            scores['leadership_score'] = ceo_analysis['analysis_summary'].get('future_impact_score', 0)
        
        # Technology score
        if 'analysis_summary' in tech_analysis:
            scores['technology_score'] = tech_analysis['analysis_summary'].get('overall_tech_score', 0)
        
        # Sentiment score (normalize to 0-10)
        if 'analysis_summary' in sentiment_analysis:
            sentiment_raw = sentiment_analysis['analysis_summary'].get('overall_sentiment_score', 0)
            # Convert from -1 to 1 range to 0-10 range
            scores['sentiment_score'] = (sentiment_raw + 1) * 5
        
        # Financial health (simplified calculation)
        profit_data = analysis_results.get('profit_analysis', {})
        if 'company_metrics' in profit_data:
            roe = profit_data['company_metrics'].get('roe')
            profit_margin = profit_data['company_metrics'].get('profit_margins_current', {}).get('profit_margin')
            
            financial_score = 5  # baseline
            if roe and roe > 0.15:
                financial_score += 2
            if profit_margin and profit_margin > 0.1:
                financial_score += 2
            
            scores['financial_health_score'] = min(financial_score, 10)
        
        # Overall investment score (weighted average)
        weights = {
            'future_focus': 0.25,
            'leadership': 0.2,
            'technology': 0.25,
            'financial': 0.2,
            'sentiment': 0.1
        }
        
        overall_score = (
            scores['future_focus_score'] * weights['future_focus'] +
            scores['leadership_score'] * weights['leadership'] +
            scores['technology_score'] * weights['technology'] +
            scores['financial_health_score'] * weights['financial'] +
            scores['sentiment_score'] * weights['sentiment']
        )
        
        scores['overall_investment_score'] = round(overall_score, 2)
        
        # Risk level assessment
        if overall_score >= 7.5:
            scores['risk_level'] = 'low'
        elif overall_score >= 5.5:
            scores['risk_level'] = 'medium'
        else:
            scores['risk_level'] = 'high'
        
        return scores
    
    def _reconstruct_analysis_from_cache(self, recent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Reconstruct analysis results from cached data"""
        metadata = recent_analysis['metadata']
        raw_data = recent_analysis['raw_data']
        
        # Create the analysis results structure
        analysis_results = {
            'ticker': metadata['ticker'],
            'analysis_timestamp': metadata['analysis_date'],
            'llm_used': metadata.get('llm_used', 'cached'),
            'company_info': {},
            'cash_flow_analysis': raw_data.get('cash_flow_analysis', {}),
            'profit_analysis': raw_data.get('profit_analysis', {}),
            'ceo_analysis': raw_data.get('ceo_analysis', {}),
            'technology_analysis': raw_data.get('technology_analysis', {}),
            'sentiment_analysis': raw_data.get('sentiment_analysis', {}),
            'llm_insights': raw_data.get('llm_insights', {}),
            'overall_scores': metadata.get('overall_scores', {}),
            'analysis_status': {},
            'analysis_duration': metadata.get('analysis_duration', 'cached'),
            'report_files': {
                'analysis_folder': recent_analysis['analysis_folder'],
                'report_file': 'See analysis folder for reports',
                'metadata_file': f"{recent_analysis['analysis_folder']}/analysis_metadata.json"
            }
        }
        
        # Set analysis status for all components that have data
        for component in ['cash_flow', 'profit', 'ceo', 'technology', 'sentiment']:
            component_key = f"{component}_analysis"
            if component_key in raw_data and raw_data[component_key]:
                analysis_results['analysis_status'][component] = 'completed (cached)'
            else:
                analysis_results['analysis_status'][component] = 'not available in cache'
        
        # Extract company info from cash flow analysis if available
        if 'cash_flow_analysis' in raw_data and 'analysis_summary' in raw_data['cash_flow_analysis']:
            analysis_results['company_info'].update(raw_data['cash_flow_analysis']['analysis_summary'])
        
        return analysis_results
    
    def get_analysis_summary(self, ticker: str) -> str:
        """Get a quick summary of the analysis results"""
        try:
            # Check if analysis exists
            import os
            reports_dir = f"reports/{ticker.upper()}"
            if not os.path.exists(reports_dir):
                return f"No analysis found for {ticker}. Run analyze_ticker_comprehensive() first."
            
            # Find the latest report file
            report_files = [f for f in os.listdir(reports_dir) if f.endswith('.md')]
            if not report_files:
                return f"No report file found for {ticker}."
            
            latest_report = max(report_files)
            report_path = os.path.join(reports_dir, latest_report)
            
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract executive summary
            if "## Executive Summary" in content:
                start_idx = content.index("## Executive Summary")
                end_idx = content.index("---", start_idx + 1)
                return content[start_idx:end_idx].strip()
            else:
                return f"Report found for {ticker}, but summary extraction failed."
                
        except Exception as e:
            return f"Error retrieving summary for {ticker}: {str(e)}"


# Convenience function for direct usage
def analyze_ticker(ticker: str, use_llm: str = "gemini", force_new: bool = False) -> Dict[str, Any]:
    """Convenience function to analyze a ticker
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        use_llm: "gemini" for Gemini Pro or "openai" for ChatGPT-4o
        force_new: If True, skip cache and run new analysis
    
    Returns:
        Complete analysis results
    """
    agent = TickerAnalyzerAgent(use_llm=use_llm)
    return agent.analyze_ticker_comprehensive(ticker, force_new=force_new)