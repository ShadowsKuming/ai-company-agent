"""
Tools Functionality Test Suite
Tests all analysis tools with sample data
Run directly: python tests/test_tools.py
"""

import os
import sys
import time
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.tool.financial_analysis import CashFlowAnalyzer, ProfitAnalyzer
    from src.tool.ceo_analysis import CEOAnalyzer
    from src.tool.technology_analysis import TechnologyAnalyzer
    from src.tool.sentiment_analysis import SentimentAnalyzer
    from src.tool.report_generator import ReportGenerator
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class ToolsTester:
    """Test all analysis tools with sample data"""
    
    def __init__(self):
        self.test_ticker = "AAPL"  # Use Apple as test case
        self.results = {
            'cash_flow_analyzer': {'status': 'not_tested', 'error': None},
            'profit_analyzer': {'status': 'not_tested', 'error': None},
            'ceo_analyzer': {'status': 'not_tested', 'error': None},
            'technology_analyzer': {'status': 'not_tested', 'error': None},
            'sentiment_analyzer': {'status': 'not_tested', 'error': None},
            'report_generator': {'status': 'not_tested', 'error': None}
        }
    
    def test_cash_flow_analyzer(self):
        """Test CashFlowAnalyzer tool"""
        print("[CASH_FLOW] Testing Cash Flow Analyzer...")
        
        try:
            analyzer = CashFlowAnalyzer()
            
            # Test financial data retrieval
            print("   Testing financial data retrieval...")
            financial_data = analyzer.get_financial_data(self.test_ticker)
            
            if 'error' in financial_data:
                self.results['cash_flow_analyzer'] = {'status': 'failed', 'error': financial_data['error']}
                print(f"   ❌ Failed to get financial data: {financial_data['error']}")
                return
            
            print(f"   ✅ Financial data retrieved for {financial_data.get('ticker', 'unknown')}")
            
            # Test revenue analysis
            print("   Testing revenue analysis...")
            revenue_analysis = analyzer.analyze_revenue_streams(financial_data)
            
            if 'error' in revenue_analysis:
                print(f"   ⚠️  Revenue analysis had issues: {revenue_analysis['error']}")
            else:
                print(f"   ✅ Revenue analysis completed")
                print(f"      Sector: {revenue_analysis.get('sector', 'N/A')}")
            
            # Test R&D analysis
            print("   Testing R&D ratio calculation...")
            rd_analysis = analyzer.calculate_rd_ratio(financial_data)
            
            if 'error' in rd_analysis:
                print(f"   ⚠️  R&D analysis had issues: {rd_analysis['error']}")
            else:
                print(f"   ✅ R&D analysis completed")
                print(f"      Future focus score: {rd_analysis.get('future_focus_score', 'N/A')}")
            
            # Test complete analysis
            print("   Testing complete cash flow analysis...")
            complete_analysis = analyzer.analyze_cash_flow(self.test_ticker)
            
            if 'error' in complete_analysis:
                self.results['cash_flow_analyzer'] = {'status': 'partial', 'error': complete_analysis['error']}
                print(f"   ⚠️  Complete analysis failed: {complete_analysis['error']}")
            else:
                self.results['cash_flow_analyzer'] = {'status': 'working', 'error': None}
                print(f"   ✅ Complete analysis successful")
                
                # Print key metrics
                if 'analysis_summary' in complete_analysis:
                    summary = complete_analysis['analysis_summary']
                    print(f"      Company: {summary.get('company_name', 'N/A')}")
                    print(f"      Future focus score: {summary.get('future_focus_score', 'N/A')}")
            
        except Exception as e:
            self.results['cash_flow_analyzer'] = {'status': 'failed', 'error': str(e)}
            print(f"   ❌ Exception: {str(e)}")
    
    def test_profit_analyzer(self):
        """Test ProfitAnalyzer tool"""
        print("[PROFIT] Testing Profit Analyzer...")
        
        try:
            analyzer = ProfitAnalyzer()
            
            print("   Testing profit mechanism analysis...")
            result = analyzer.analyze_profit_mechanisms(self.test_ticker)
            
            if 'error' in result:
                self.results['profit_analyzer'] = {'status': 'failed', 'error': result['error']}
                print(f"   ❌ Failed: {result['error']}")
            else:
                self.results['profit_analyzer'] = {'status': 'working', 'error': None}
                print(f"   ✅ Profit analysis successful")
                
                # Check key components
                if 'profit_margins' in result:
                    margins_count = len(result['profit_margins'])
                    print(f"      Profit margins data: {margins_count} periods")
                
                if 'company_metrics' in result:
                    metrics = result['company_metrics']
                    roe = metrics.get('roe', 'N/A')
                    print(f"      ROE: {roe}")
            
        except Exception as e:
            self.results['profit_analyzer'] = {'status': 'failed', 'error': str(e)}
            print(f"   ❌ Exception: {str(e)}")
    
    def test_ceo_analyzer(self):
        """Test CEOAnalyzer tool"""
        print("[CEO] Testing CEO Analyzer...")
        
        try:
            analyzer = CEOAnalyzer()
            
            # Test company leadership info
            print("   Testing company leadership retrieval...")
            leadership_info = analyzer.get_company_leadership(self.test_ticker)
            
            if 'error' in leadership_info:
                print(f"   ⚠️  Leadership info issue: {leadership_info['error']}")
            else:
                ceo_name = leadership_info.get('ceo_name', 'N/A')
                company_name = leadership_info.get('company_name', 'N/A')
                print(f"   ✅ Leadership info retrieved")
                print(f"      Company: {company_name}")
                print(f"      CEO: {ceo_name}")
            
            # Test complete CEO analysis (this may take time due to web searches)
            print("   Testing complete CEO analysis (may take 30-60 seconds)...")
            start_time = time.time()
            
            result = analyzer.analyze_ceo_complete(self.test_ticker)
            analysis_time = time.time() - start_time
            
            if 'error' in result:
                self.results['ceo_analyzer'] = {'status': 'partial', 'error': result['error']}
                print(f"   ⚠️  Partial success: {result['error']}")
            else:
                self.results['ceo_analyzer'] = {'status': 'working', 'error': None}
                print(f"   ✅ Complete analysis successful ({analysis_time:.1f}s)")
                
                # Check results
                if 'analysis_summary' in result:
                    summary = result['analysis_summary']
                    impact_score = summary.get('future_impact_score', 'N/A')
                    strengths = len(summary.get('key_strengths', []))
                    print(f"      Future impact score: {impact_score}")
                    print(f"      Key strengths identified: {strengths}")
            
        except Exception as e:
            self.results['ceo_analyzer'] = {'status': 'failed', 'error': str(e)}
            print(f"   ❌ Exception: {str(e)}")
    
    def test_technology_analyzer(self):
        """Test TechnologyAnalyzer tool"""
        print("[TECH] Testing Technology Analyzer...")
        
        try:
            analyzer = TechnologyAnalyzer()
            
            # Test company tech info
            print("   Testing company tech info retrieval...")
            tech_info = analyzer.get_company_tech_info(self.test_ticker)
            
            if 'error' in tech_info:
                print(f"   ⚠️  Tech info issue: {tech_info['error']}")
            else:
                company_name = tech_info.get('company_name', 'N/A')
                sector = tech_info.get('sector', 'N/A')
                print(f"   ✅ Tech info retrieved")
                print(f"      Company: {company_name}")
                print(f"      Sector: {sector}")
            
            # Test complete technology analysis (may take time due to web searches)
            print("   Testing complete technology analysis (may take 30-60 seconds)...")
            start_time = time.time()
            
            result = analyzer.analyze_technology_complete(self.test_ticker)
            analysis_time = time.time() - start_time
            
            if 'error' in result:
                self.results['technology_analyzer'] = {'status': 'partial', 'error': result['error']}
                print(f"   ⚠️  Partial success: {result['error']}")
            else:
                self.results['technology_analyzer'] = {'status': 'working', 'error': None}
                print(f"   ✅ Complete analysis successful ({analysis_time:.1f}s)")
                
                # Check results
                if 'analysis_summary' in result:
                    summary = result['analysis_summary']
                    tech_score = summary.get('overall_tech_score', 'N/A')
                    strengths = len(summary.get('key_strengths', []))
                    focus_areas = len(summary.get('technology_focus_areas', []))
                    print(f"      Technology score: {tech_score}")
                    print(f"      Key strengths: {strengths}")
                    print(f"      Focus areas identified: {focus_areas}")
            
        except Exception as e:
            self.results['technology_analyzer'] = {'status': 'failed', 'error': str(e)}
            print(f"   ❌ Exception: {str(e)}")
    
    def test_sentiment_analyzer(self):
        """Test SentimentAnalyzer tool"""
        print("[SENTIMENT] Testing Sentiment Analyzer...")
        
        try:
            analyzer = SentimentAnalyzer()
            
            # Test company info retrieval
            print("   Testing company info retrieval...")
            company_info = analyzer.get_company_info(self.test_ticker)
            
            if 'error' in company_info:
                print(f"   ⚠️  Company info issue: {company_info['error']}")
            else:
                company_name = company_info.get('company_name', 'N/A')
                print(f"   ✅ Company info retrieved: {company_name}")
            
            # Test complete sentiment analysis (may take time due to searches)
            print("   Testing complete sentiment analysis (may take 30-60 seconds)...")
            start_time = time.time()
            
            result = analyzer.analyze_sentiment_complete(self.test_ticker)
            analysis_time = time.time() - start_time
            
            if 'error' in result:
                self.results['sentiment_analyzer'] = {'status': 'partial', 'error': result['error']}
                print(f"   ⚠️  Partial success: {result['error']}")
            else:
                self.results['sentiment_analyzer'] = {'status': 'working', 'error': None}
                print(f"   ✅ Complete analysis successful ({analysis_time:.1f}s)")
                
                # Check results
                if 'analysis_summary' in result:
                    summary = result['analysis_summary']
                    sentiment_score = summary.get('overall_sentiment_score', 'N/A')
                    sentiment_category = summary.get('sentiment_category', 'N/A')
                    confidence = summary.get('confidence_level', 'N/A')
                    data_quality = summary.get('data_quality', {})
                    
                    print(f"      Sentiment score: {sentiment_score}")
                    print(f"      Sentiment category: {sentiment_category}")
                    print(f"      Confidence: {confidence}")
                    print(f"      News articles: {data_quality.get('news_articles_analyzed', 0)}")
                    print(f"      Tweets: {data_quality.get('tweets_analyzed', 0)}")
            
        except Exception as e:
            self.results['sentiment_analyzer'] = {'status': 'failed', 'error': str(e)}
            print(f"   ❌ Exception: {str(e)}")
    
    def test_report_generator(self):
        """Test ReportGenerator tool"""
        print("[REPORT] Testing Report Generator...")
        
        try:
            generator = ReportGenerator()
            
            # Test folder creation
            print("   Testing ticker folder creation...")
            folder_path = generator.create_ticker_folder(self.test_ticker)
            print(f"   ✅ Folder created: {folder_path}")
            
            # Test with sample analysis data
            print("   Testing report generation with sample data...")
            sample_data = {
                'ticker': self.test_ticker,
                'company_info': {
                    'company_name': 'Apple Inc.',
                    'sector': 'Technology'
                },
                'cash_flow_analysis': {
                    'analysis_summary': {
                        'future_focus_score': 8.5,
                        'company_name': 'Apple Inc.'
                    }
                },
                'sentiment_analysis': {
                    'analysis_summary': {
                        'overall_sentiment_score': 0.3,
                        'sentiment_category': 'positive'
                    }
                }
            }
            
            # Test raw data saving
            print("   Testing raw data saving...")
            raw_file = generator.save_raw_data(self.test_ticker, 'test_analysis', sample_data)
            print(f"   ✅ Raw data saved: {os.path.basename(raw_file)}")
            
            # Test markdown report generation
            print("   Testing markdown report generation...")
            report_file = generator.generate_markdown_report(self.test_ticker, sample_data)
            print(f"   ✅ Markdown report generated: {os.path.basename(report_file)}")
            
            # Test complete report generation
            print("   Testing complete report generation...")
            complete_result = generator.generate_complete_report(self.test_ticker, sample_data)
            
            if 'error' in complete_result:
                self.results['report_generator'] = {'status': 'partial', 'error': complete_result['error']}
                print(f"   ⚠️  Partial success: {complete_result['error']}")
            else:
                self.results['report_generator'] = {'status': 'working', 'error': None}
                print(f"   ✅ Complete report generation successful")
                print(f"      Report file: {os.path.basename(complete_result.get('report_file', 'N/A'))}")
                print(f"      Raw data files: {len(complete_result.get('raw_data_files', {}))}")
            
        except Exception as e:
            self.results['report_generator'] = {'status': 'failed', 'error': str(e)}
            print(f"   ❌ Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tool tests"""
        print("[TOOLS] Starting Tools Functionality Tests")
        print(f"[TARGET] Test ticker: {self.test_ticker}")
        print("=" * 60)
        
        # Run tests
        self.test_cash_flow_analyzer()
        print()
        self.test_profit_analyzer()
        print()
        self.test_ceo_analyzer()
        print()
        self.test_technology_analyzer()
        print()
        self.test_sentiment_analyzer()
        print()
        self.test_report_generator()
        
        print("\n" + "=" * 60)
        print("[SUMMARY] Tools Test Results Summary")
        print("=" * 60)
        
        # Count results
        working = 0
        partial = 0
        failed = 0
        
        for tool_name, result in self.results.items():
            status = result['status']
            error = result['error']
            
            if status == 'working':
                print(f"[OK] {tool_name}: Working")
                working += 1
            elif status == 'partial':
                print(f"[WARN] {tool_name}: Partial - {error}")
                partial += 1
            elif status == 'failed':
                print(f"[FAIL] {tool_name}: Failed - {error}")
                failed += 1
            else:
                print(f"[UNKNOWN] {tool_name}: Not tested")
                failed += 1
        
        total = working + partial + failed
        print(f"\n[STATUS] Overall Status: {working}/{total} fully working, {partial} partial, {failed} failed")
        
        print("\n[ANALYSIS] Analysis:")
        
        if working >= 4:
            print("[OK] Most tools are working properly. System should function well.")
        elif working >= 2:
            print("[WARN] Some tools working. Core functionality available but limited.")
        else:
            print("[CRITICAL] Most tools failing. Check API keys and network connectivity.")
        
        # Specific recommendations
        if self.results['cash_flow_analyzer']['status'] == 'failed':
            print("[ERROR] Cash flow analyzer failed - financial analysis will not work")
        
        if (self.results['ceo_analyzer']['status'] == 'failed' and 
            self.results['technology_analyzer']['status'] == 'failed' and
            self.results['sentiment_analyzer']['status'] == 'failed'):
            print("[ERROR] All web-dependent tools failed - check search API keys")
        
        if self.results['report_generator']['status'] == 'failed':
            print("[ERROR] Report generator failed - no reports will be saved")
        
        return self.results


def main():
    """Main test runner"""
    tester = ToolsTester()
    results = tester.run_all_tests()
    
    # Count working tools
    working = sum(1 for result in results.values() if result['status'] == 'working')
    partial = sum(1 for result in results.values() if result['status'] == 'partial')
    total = len(results)
    
    # Critical tools that must work
    critical_tools = ['cash_flow_analyzer', 'report_generator']
    critical_working = sum(1 for tool in critical_tools if results[tool]['status'] in ['working', 'partial'])
    
    if critical_working < len(critical_tools):
        print(f"\n[FAIL] Test failed: Critical tools not working ({critical_working}/{len(critical_tools)})")
        sys.exit(1)
    elif working + partial >= total * 0.5:  # At least 50% working
        print(f"\n[OK] Test passed: {working + partial}/{total} tools functional")
        sys.exit(0)
    else:
        print(f"\n[WARN] Test completed with warnings: {working + partial}/{total} tools functional")
        sys.exit(1)


if __name__ == "__main__":
    main()