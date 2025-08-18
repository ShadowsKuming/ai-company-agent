"""
Agents Functionality Test Suite
Tests both TickerAnalyzer and InvestmentRecommender agents end-to-end
Run directly: python tests/test_agents.py
"""

import os
import sys
import time
import shutil
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.agent.ticker_analyzer import TickerAnalyzerAgent, analyze_ticker
    from src.agent.investment_recommender import InvestmentRecommenderAgent, get_investment_recommendation
    from src.config import GEMINI_API_KEY, OPENAI_API_KEY
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class AgentsTester:
    """Test both main agents with end-to-end workflows"""
    
    def __init__(self):
        self.test_ticker = "AAPL"  # Use Apple as test case
        self.test_timeout = 300  # 5 minutes timeout for full analysis
        
        self.results = {
            'ticker_analyzer_gemini': {'status': 'not_tested', 'error': None},
            'ticker_analyzer_openai': {'status': 'not_tested', 'error': None},
            'investment_recommender_gemini': {'status': 'not_tested', 'error': None},
            'investment_recommender_openai': {'status': 'not_tested', 'error': None}
        }
        
        # Clean up any existing test reports
        self.cleanup_test_reports()
    
    def cleanup_test_reports(self):
        """Clean up any existing test reports"""
        try:
            reports_dir = f"reports/{self.test_ticker}"
            if os.path.exists(reports_dir):
                shutil.rmtree(reports_dir)
                print(f"🧹 Cleaned up existing reports for {self.test_ticker}")
        except Exception as e:
            print(f"⚠️  Could not clean up reports: {e}")
    
    def test_ticker_analyzer_agent(self, llm_type='gemini'):
        """Test TickerAnalyzerAgent with specified LLM"""
        print(f"🎯 Testing Ticker Analyzer Agent ({llm_type.upper()})...")
        
        result_key = f'ticker_analyzer_{llm_type}'
        
        # Check if LLM is available
        if llm_type == 'gemini' and not GEMINI_API_KEY:
            self.results[result_key] = {'status': 'skipped', 'error': 'No Gemini API key'}
            print("   ⚠️  Skipping - No Gemini API key")
            return
        elif llm_type == 'openai' and not OPENAI_API_KEY:
            self.results[result_key] = {'status': 'skipped', 'error': 'No OpenAI API key'}
            print("   ⚠️  Skipping - No OpenAI API key")
            return
        
        try:
            # Initialize agent
            print(f"   📡 Initializing TickerAnalyzerAgent with {llm_type}...")
            agent = TickerAnalyzerAgent(use_llm=llm_type)
            print(f"   ✅ Agent initialized successfully")
            
            # Test comprehensive analysis
            print(f"   🔍 Running comprehensive analysis for {self.test_ticker}...")
            print(f"      (This may take 2-5 minutes depending on API response times)")
            
            start_time = time.time()
            analysis_result = agent.analyze_ticker_comprehensive(self.test_ticker)
            analysis_time = time.time() - start_time
            
            # Check if analysis completed successfully
            if 'error' in analysis_result:
                self.results[result_key] = {
                    'status': 'failed', 
                    'error': analysis_result['error'],
                    'analysis_time': analysis_time
                }
                print(f"   ❌ Analysis failed: {analysis_result['error']}")
                return
            
            # Validate analysis results
            validation_results = self.validate_analysis_result(analysis_result)
            
            if validation_results['critical_failures'] > 0:
                self.results[result_key] = {
                    'status': 'partial',
                    'error': f"{validation_results['critical_failures']} critical component(s) failed",
                    'analysis_time': analysis_time,
                    'validation': validation_results
                }
                print(f"   ⚠️  Analysis partial: {validation_results['critical_failures']} critical failures")
            else:
                self.results[result_key] = {
                    'status': 'working',
                    'error': None,
                    'analysis_time': analysis_time,
                    'validation': validation_results
                }
                print(f"   ✅ Analysis successful ({analysis_time:.1f}s)")
            
            # Print key results
            overall_scores = analysis_result.get('overall_scores', {})
            if overall_scores:
                print(f"      Overall investment score: {overall_scores.get('overall_investment_score', 'N/A')}")
                print(f"      Risk level: {overall_scores.get('risk_level', 'N/A')}")
            
            # Check report generation
            report_files = analysis_result.get('report_files', {})
            if 'report_file' in report_files:
                print(f"      Report generated: {os.path.basename(report_files['report_file'])}")
            
        except Exception as e:
            self.results[result_key] = {
                'status': 'failed',
                'error': str(e),
                'analysis_time': time.time() - start_time if 'start_time' in locals() else 0
            }
            print(f"   ❌ Exception: {str(e)}")
    
    def validate_analysis_result(self, result):
        """Validate the completeness of analysis results"""
        validation = {
            'components_tested': 0,
            'components_passed': 0,
            'critical_failures': 0,
            'warnings': []
        }
        
        # Critical components that must work
        critical_components = [
            'cash_flow_analysis',
            'overall_scores',
            'analysis_timestamp'
        ]
        
        # All expected components
        expected_components = [
            'cash_flow_analysis',
            'profit_analysis', 
            'ceo_analysis',
            'technology_analysis',
            'sentiment_analysis',
            'overall_scores',
            'report_files'
        ]
        
        for component in expected_components:
            validation['components_tested'] += 1
            
            if component in result and result[component]:
                # Check if component has error
                if isinstance(result[component], dict) and 'error' not in result[component]:
                    validation['components_passed'] += 1
                elif isinstance(result[component], dict) and 'error' in result[component]:
                    validation['warnings'].append(f"{component} has errors")
                    if component in critical_components:
                        validation['critical_failures'] += 1
                else:
                    validation['components_passed'] += 1
            else:
                validation['warnings'].append(f"{component} missing or empty")
                if component in critical_components:
                    validation['critical_failures'] += 1
        
        return validation
    
    def test_investment_recommender_agent(self, llm_type='gemini'):
        """Test InvestmentRecommenderAgent with specified LLM"""
        print(f"💡 Testing Investment Recommender Agent ({llm_type.upper()})...")
        
        result_key = f'investment_recommender_{llm_type}'
        
        # Check if LLM is available
        if llm_type == 'gemini' and not GEMINI_API_KEY:
            self.results[result_key] = {'status': 'skipped', 'error': 'No Gemini API key'}
            print("   ⚠️  Skipping - No Gemini API key")
            return
        elif llm_type == 'openai' and not OPENAI_API_KEY:
            self.results[result_key] = {'status': 'skipped', 'error': 'No OpenAI API key'}
            print("   ⚠️  Skipping - No OpenAI API key")
            return
        
        # Check if ticker analysis exists (prerequisite)
        reports_dir = f"reports/{self.test_ticker}/raw_data"
        if not os.path.exists(reports_dir):
            self.results[result_key] = {
                'status': 'skipped', 
                'error': 'No analysis data available. Run ticker analyzer first.'
            }
            print("   ⚠️  Skipping - No analysis data available")
            return
        
        try:
            # Initialize agent
            print(f"   📡 Initializing InvestmentRecommenderAgent with {llm_type}...")
            agent = InvestmentRecommenderAgent(use_llm=llm_type)
            print(f"   ✅ Agent initialized successfully")
            
            # Test recommendation generation
            print(f"   🎯 Generating investment recommendation for {self.test_ticker}...")
            
            start_time = time.time()
            recommendation_result = agent.recommend_investment(self.test_ticker)
            recommendation_time = time.time() - start_time
            
            # Check if recommendation completed successfully
            if 'error' in recommendation_result:
                self.results[result_key] = {
                    'status': 'failed',
                    'error': recommendation_result['error'],
                    'recommendation_time': recommendation_time
                }
                print(f"   ❌ Recommendation failed: {recommendation_result['error']}")
                return
            
            # Validate recommendation results
            validation_results = self.validate_recommendation_result(recommendation_result)
            
            if validation_results['critical_failures'] > 0:
                self.results[result_key] = {
                    'status': 'partial',
                    'error': f"{validation_results['critical_failures']} critical component(s) failed",
                    'recommendation_time': recommendation_time,
                    'validation': validation_results
                }
                print(f"   ⚠️  Recommendation partial: {validation_results['critical_failures']} critical failures")
            else:
                self.results[result_key] = {
                    'status': 'working',
                    'error': None,
                    'recommendation_time': recommendation_time,
                    'validation': validation_results
                }
                print(f"   ✅ Recommendation successful ({recommendation_time:.1f}s)")
            
            # Print key results
            recommendation = recommendation_result.get('recommendation', 'N/A')
            score = recommendation_result.get('overall_score', 'N/A')
            confidence = recommendation_result.get('confidence_level', 'N/A')
            
            print(f"      Recommendation: {recommendation}")
            print(f"      Score: {score}")
            print(f"      Confidence: {confidence}")
            
            # Check report generation
            if 'report_path' in recommendation_result:
                print(f"      Report saved: {os.path.basename(recommendation_result['report_path'])}")
            
        except Exception as e:
            self.results[result_key] = {
                'status': 'failed',
                'error': str(e),
                'recommendation_time': time.time() - start_time if 'start_time' in locals() else 0
            }
            print(f"   ❌ Exception: {str(e)}")
    
    def validate_recommendation_result(self, result):
        """Validate the completeness of recommendation results"""
        validation = {
            'components_tested': 0,
            'components_passed': 0,
            'critical_failures': 0,
            'warnings': []
        }
        
        # Expected components in recommendation
        expected_components = [
            'recommendation',
            'overall_score',
            'confidence_level',
            'detailed_scores',
            'key_risks',
            'key_opportunities',
            'llm_reasoning'
        ]
        
        # Critical components
        critical_components = [
            'recommendation',
            'overall_score',
            'confidence_level'
        ]
        
        for component in expected_components:
            validation['components_tested'] += 1
            
            if component in result and result[component] is not None:
                validation['components_passed'] += 1
            else:
                validation['warnings'].append(f"{component} missing or empty")
                if component in critical_components:
                    validation['critical_failures'] += 1
        
        # Validate recommendation value
        if 'recommendation' in result:
            valid_recommendations = ['STRONG BUY', 'BUY', 'HOLD', 'WEAK HOLD', 'SELL']
            if result['recommendation'] not in valid_recommendations:
                validation['warnings'].append("Invalid recommendation value")
        
        # Validate score range
        if 'overall_score' in result:
            try:
                score = float(result['overall_score'])
                if not (0 <= score <= 10):
                    validation['warnings'].append("Score out of valid range (0-10)")
            except (ValueError, TypeError):
                validation['warnings'].append("Invalid score format")
        
        return validation
    
    def test_convenience_functions(self):
        """Test convenience functions for quick usage"""
        print("🔧 Testing Convenience Functions...")
        
        if not GEMINI_API_KEY and not OPENAI_API_KEY:
            print("   ⚠️  Skipping - No LLM APIs available")
            return
        
        llm_to_use = 'gemini' if GEMINI_API_KEY else 'openai'
        
        try:
            # Test analyze_ticker function
            print(f"   Testing analyze_ticker() function with {llm_to_use}...")
            result = analyze_ticker(self.test_ticker, use_llm=llm_to_use)
            
            if 'error' in result:
                print(f"   ⚠️  analyze_ticker() had issues: {result['error']}")
            else:
                print(f"   ✅ analyze_ticker() working")
            
            # Test get_investment_recommendation function
            print(f"   Testing get_investment_recommendation() function...")
            recommendation = get_investment_recommendation(self.test_ticker, use_llm=llm_to_use)
            
            if 'error' in recommendation:
                print(f"   ⚠️  get_investment_recommendation() had issues: {recommendation['error']}")
            else:
                print(f"   ✅ get_investment_recommendation() working")
                print(f"      Quick result: {recommendation.get('recommendation', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Convenience functions failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all agent tests"""
        print("🚀 Starting Agents Functionality Tests")
        print(f"🎯 Test ticker: {self.test_ticker}")
        print(f"⏰ Timeout per test: {self.test_timeout}s")
        print("=" * 60)
        
        # Test TickerAnalyzer with both LLMs
        if GEMINI_API_KEY:
            self.test_ticker_analyzer_agent('gemini')
            print()
        
        if OPENAI_API_KEY:
            self.test_ticker_analyzer_agent('openai')
            print()
        
        # Test InvestmentRecommender with both LLMs
        if GEMINI_API_KEY:
            self.test_investment_recommender_agent('gemini')
            print()
        
        if OPENAI_API_KEY:
            self.test_investment_recommender_agent('openai')
            print()
        
        # Test convenience functions
        self.test_convenience_functions()
        
        print("\n" + "=" * 60)
        print("📋 Agents Test Results Summary")
        print("=" * 60)
        
        # Count results
        working = 0
        partial = 0
        failed = 0
        skipped = 0
        
        for agent_name, result in self.results.items():
            status = result['status']
            error = result['error']
            
            if status == 'working':
                print(f"✅ {agent_name}: Working")
                working += 1
                if 'analysis_time' in result:
                    print(f"   ⏱️  Analysis time: {result['analysis_time']:.1f}s")
                elif 'recommendation_time' in result:
                    print(f"   ⏱️  Recommendation time: {result['recommendation_time']:.1f}s")
            elif status == 'partial':
                print(f"⚠️  {agent_name}: Partial - {error}")
                partial += 1
            elif status == 'failed':
                print(f"❌ {agent_name}: Failed - {error}")
                failed += 1
            elif status == 'skipped':
                print(f"⏭️  {agent_name}: Skipped - {error}")
                skipped += 1
            else:
                print(f"❓ {agent_name}: Not tested")
                failed += 1
        
        tested = working + partial + failed
        total = tested + skipped
        
        print(f"\n📊 Overall Status: {working}/{tested} fully working, {partial} partial, {failed} failed")
        print(f"📊 Coverage: {tested}/{total} agents tested, {skipped} skipped")
        
        print("\n💡 Analysis:")
        
        # Check if at least one complete workflow works
        ticker_working = any(
            self.results[key]['status'] in ['working', 'partial'] 
            for key in self.results 
            if 'ticker_analyzer' in key
        )
        
        recommender_working = any(
            self.results[key]['status'] in ['working', 'partial'] 
            for key in self.results 
            if 'investment_recommender' in key
        )
        
        if ticker_working and recommender_working:
            print("✅ Complete end-to-end workflow functional")
        elif ticker_working:
            print("⚠️  Ticker analysis working but recommendation may have issues")
        elif recommender_working:
            print("⚠️  Recommendation working but requires pre-existing analysis data")
        else:
            print("❌ Critical: No complete workflows functional")
        
        # Performance analysis
        analysis_times = [
            result.get('analysis_time', 0) 
            for result in self.results.values() 
            if result.get('analysis_time', 0) > 0
        ]
        
        if analysis_times:
            avg_time = sum(analysis_times) / len(analysis_times)
            print(f"⏱️  Average analysis time: {avg_time:.1f}s")
            
            if avg_time > 300:  # 5 minutes
                print("⚠️  Analysis is slow - consider optimizing API calls")
        
        return self.results


def main():
    """Main test runner"""
    tester = AgentsTester()
    results = tester.run_all_tests()
    
    # Check if core functionality works
    ticker_working = any(
        results[key]['status'] in ['working', 'partial'] 
        for key in results 
        if 'ticker_analyzer' in key
    )
    
    if not ticker_working:
        print(f"\n❌ Test failed: No ticker analyzer agents working")
        sys.exit(1)
    
    # Count overall functionality
    working = sum(1 for result in results.values() if result['status'] == 'working')
    partial = sum(1 for result in results.values() if result['status'] == 'partial')
    tested = sum(1 for result in results.values() if result['status'] != 'skipped')
    
    if working > 0:
        print(f"\n✅ Test passed: {working + partial}/{tested} agents functional")
        sys.exit(0)
    else:
        print(f"\n❌ Test failed: No agents fully functional")
        sys.exit(1)


if __name__ == "__main__":
    main()