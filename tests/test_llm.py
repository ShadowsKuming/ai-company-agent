"""
LLM Functionality Test Suite
Tests both Gemini and OpenAI LLM integrations with various prompts
Run directly: python tests/test_llm.py
"""

import os
import sys
import time
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.config import (
        GEMINI_API_KEY, 
        OPENAI_API_KEY,
        get_gemini_model,
        get_openai_model
    )
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class LLMTester:
    """Test LLM functionality with various types of prompts"""
    
    def __init__(self):
        self.test_prompts = {
            'simple_response': {
                'prompt': 'Respond with exactly "TEST_OK" if you understand this message.',
                'expected_contains': ['TEST_OK'],
                'description': 'Simple response test'
            },
            'financial_analysis': {
                'prompt': '''Analyze this financial data and provide a brief summary:
                Company: Apple Inc
                Revenue Growth: 8.2%
                R&D Spending: 15% of revenue
                Provide a 2-sentence analysis focusing on innovation investment.''',
                'expected_contains': ['Apple', 'R&D', 'innovation'],
                'description': 'Financial analysis capability'
            },
            'structured_output': {
                'prompt': '''Rate the following company attributes on a scale of 1-10 and respond in this exact format:
                Growth: [score]
                Innovation: [score]
                
                Company: Tesla
                Recent developments: Strong EV sales, AI development, energy storage growth''',
                'expected_contains': ['Growth:', 'Innovation:'],
                'description': 'Structured output generation'
            },
            'sentiment_analysis': {
                'prompt': '''Analyze the sentiment of this text and categorize as positive, negative, or neutral:
                "Tesla reports record quarterly earnings beating expectations. CEO announces major expansion in renewable energy sector."
                
                Respond with: Sentiment: [category]''',
                'expected_contains': ['Sentiment:', 'positive'],
                'description': 'Sentiment analysis task'
            },
            'reasoning_task': {
                'prompt': '''Given these investment factors for a company:
                - R&D Investment: High (18% of revenue)
                - Market Position: Strong leader
                - CEO Rating: 8/10
                - Debt Level: Low
                
                Provide a brief investment recommendation (Buy/Hold/Sell) with one reason.''',
                'expected_contains': ['Buy', 'Hold', 'Sell'],
                'description': 'Investment reasoning task'
            }
        }
        
        self.results = {
            'gemini': {},
            'openai': {}
        }
    
    def test_llm_response(self, llm_type, model, prompt_name, prompt_data):
        """Test a specific LLM with a given prompt"""
        prompt = prompt_data['prompt']
        expected = prompt_data['expected_contains']
        description = prompt_data['description']
        
        print(f"   Testing: {description}")
        
        try:
            start_time = time.time()
            
            if llm_type == 'gemini':
                response = model.generate_content(prompt)
                response_text = response.text if response else None
            elif llm_type == 'openai':
                response = model.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful financial analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200
                )
                response_text = response.choices[0].message.content if response.choices else None
            
            response_time = time.time() - start_time
            
            if not response_text:
                self.results[llm_type][prompt_name] = {
                    'status': 'failed',
                    'error': 'No response received',
                    'response_time': response_time
                }
                print(f"     [FAIL] No response received")
                return
            
            # Check if response contains expected elements
            response_lower = response_text.lower()
            found_expected = sum(1 for exp in expected if exp.lower() in response_lower)
            
            if found_expected >= len(expected) * 0.5:  # At least 50% of expected elements
                self.results[llm_type][prompt_name] = {
                    'status': 'passed',
                    'response': response_text[:200] + '...' if len(response_text) > 200 else response_text,
                    'response_time': response_time,
                    'found_expected': f"{found_expected}/{len(expected)}"
                }
                print(f"     [OK] Passed ({found_expected}/{len(expected)} expected elements) - {response_time:.2f}s")
            else:
                self.results[llm_type][prompt_name] = {
                    'status': 'partial',
                    'response': response_text[:200] + '...' if len(response_text) > 200 else response_text,
                    'response_time': response_time,
                    'found_expected': f"{found_expected}/{len(expected)}",
                    'error': f'Expected elements not found: {expected}'
                }
                print(f"     [WARN] Partial ({found_expected}/{len(expected)} expected elements) - {response_time:.2f}s")
            
        except Exception as e:
            self.results[llm_type][prompt_name] = {
                'status': 'failed',
                'error': str(e),
                'response_time': time.time() - start_time
            }
            print(f"     [FAIL] Failed: {str(e)}")
    
    def test_gemini_llm(self):
        """Test Gemini LLM functionality"""
        print("[GEMINI] Testing Gemini LLM Functionality...")
        
        if not GEMINI_API_KEY:
            print("   [WARN] Skipping - No API key found")
            self.results['gemini']['status'] = 'skipped_no_key'
            return
        
        try:
            model = get_gemini_model()
            print(f"   [CONN] Model loaded successfully")
            
            for prompt_name, prompt_data in self.test_prompts.items():
                self.test_llm_response('gemini', model, prompt_name, prompt_data)
            
        except Exception as e:
            print(f"   [FAIL] Failed to initialize Gemini: {str(e)}")
            self.results['gemini']['status'] = 'init_failed'
            self.results['gemini']['error'] = str(e)
    
    def test_openai_llm(self):
        """Test OpenAI LLM functionality"""
        print("[OPENAI] Testing OpenAI LLM Functionality...")
        
        if not OPENAI_API_KEY:
            print("   [WARN] Skipping - No API key found")
            self.results['openai']['status'] = 'skipped_no_key'
            return
        
        try:
            model = get_openai_model()
            print(f"   [CONN] Client initialized successfully")
            
            for prompt_name, prompt_data in self.test_prompts.items():
                self.test_llm_response('openai', model, prompt_name, prompt_data)
            
        except Exception as e:
            print(f"   [FAIL] Failed to initialize OpenAI: {str(e)}")
            self.results['openai']['status'] = 'init_failed'
            self.results['openai']['error'] = str(e)
    
    def run_all_tests(self):
        """Run all LLM tests"""
        print("="*60)
        print("LLM FUNCTIONALITY TESTS")
        print("="*60)
        
        self.test_gemini_llm()
        print()
        self.test_openai_llm()
        
        print("\n" + "="*60)
        print("LLM TEST RESULTS SUMMARY")
        print("="*60)
        
        # Summary for each LLM
        for llm_name in ['gemini', 'openai']:
            llm_results = self.results[llm_name]
            
            if llm_results.get('status') == 'skipped_no_key':
                print(f"[KEY] {llm_name.upper()}: Skipped (No API key)")
                continue
            elif llm_results.get('status') == 'init_failed':
                print(f"[FAIL] {llm_name.upper()}: Failed to initialize - {llm_results.get('error', 'Unknown error')}")
                continue
            
            # Count test results
            passed = sum(1 for k, v in llm_results.items() if k != 'status' and v.get('status') == 'passed')
            partial = sum(1 for k, v in llm_results.items() if k != 'status' and v.get('status') == 'partial')
            failed = sum(1 for k, v in llm_results.items() if k != 'status' and v.get('status') == 'failed')
            total = passed + partial + failed
            
            if total > 0:
                print(f"[STATS] {llm_name.upper()}: {passed}/{total} passed, {partial} partial, {failed} failed")
                
                # Average response time
                times = [v.get('response_time', 0) for k, v in llm_results.items() 
                        if k != 'status' and 'response_time' in v]
                if times:
                    avg_time = sum(times) / len(times)
                    print(f"   [TIME] Average response time: {avg_time:.2f}s")
            else:
                print(f"[UNKNOWN] {llm_name.upper()}: No tests completed")
        
        print("\nRECOMMENDATIONS:")
        
        # Check if at least one LLM is working
        working_llms = []
        for llm_name in ['gemini', 'openai']:
            llm_results = self.results[llm_name]
            if llm_results.get('status') not in ['skipped_no_key', 'init_failed']:
                passed = sum(1 for k, v in llm_results.items() if k != 'status' and v.get('status') in ['passed', 'partial'])
                if passed > 0:
                    working_llms.append(llm_name)
        
        if not working_llms:
            print("CRITICAL: No LLMs are working properly. Check API keys and network connectivity.")
        elif len(working_llms) == 1:
            print(f"OK: {working_llms[0].upper()} is working. Consider adding the other LLM as backup.")
        else:
            print("EXCELLENT: Both LLMs are working. You can use either as primary or backup.")
        
        return self.results


def main():
    """Main test runner"""
    tester = LLMTester()
    results = tester.run_all_tests()
    
    # Check if at least one LLM is functional
    working_llms = 0
    for llm_name in ['gemini', 'openai']:
        llm_results = results[llm_name]
        if llm_results.get('status') not in ['skipped_no_key', 'init_failed']:
            passed = sum(1 for k, v in llm_results.items() if k != 'status' and v.get('status') in ['passed', 'partial'])
            if passed > 0:
                working_llms += 1
    
    if working_llms == 0:
        print(f"\n[FAIL] Test failed: No LLMs are functional")
        sys.exit(1)
    else:
        print(f"\n[OK] Test passed: {working_llms} LLM(s) functional")
        sys.exit(0)


if __name__ == "__main__":
    main()