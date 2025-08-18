"""
API Connectivity Test Suite
Tests all API connections and reports which ones are working/failing
Run directly: python tests/test_apis.py
"""

import os
import sys
import requests
import yfinance as yf
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.config import (
        GEMINI_API_KEY, 
        OPENAI_API_KEY, 
        SERPAPI_API_KEY, 
        SERPER_API_KEY,
        get_gemini_model,
        get_openai_model
    )
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class APITester:
    """Test all API connections and functionality"""
    
    def __init__(self):
        self.results = {
            'gemini': {'status': 'not_tested', 'error': None},
            'openai': {'status': 'not_tested', 'error': None},
            'yfinance': {'status': 'not_tested', 'error': None},
            'serper': {'status': 'not_tested', 'error': None},
            'serpapi': {'status': 'not_tested', 'error': None},
            'twitter': {'status': 'not_tested', 'error': None}
        }
    
    def test_gemini_api(self):
        """Test Gemini API connectivity"""
        print("[GEMINI] Testing Gemini API...")
        
        if not GEMINI_API_KEY:
            self.results['gemini'] = {'status': 'missing_key', 'error': 'GEMINI_API_KEY not found in environment'}
            print("   [FAIL] Missing API key")
            return
        
        try:
            model = get_gemini_model()
            response = model.generate_content("Test message: respond with 'OK'")
            
            if response and response.text:
                self.results['gemini'] = {'status': 'working', 'error': None}
                print(f"   [OK] Working - Response: {response.text[:50]}...")
            else:
                self.results['gemini'] = {'status': 'failed', 'error': 'No response received'}
                print("   [FAIL] No response received")
                
        except Exception as e:
            self.results['gemini'] = {'status': 'failed', 'error': str(e)}
            print(f"   [FAIL] Error: {str(e)}")
    
    def test_openai_api(self):
        """Test OpenAI API connectivity"""
        print("[OPENAI] Testing OpenAI API...")
        
        if not OPENAI_API_KEY:
            self.results['openai'] = {'status': 'missing_key', 'error': 'OPENAI_API_KEY not found in environment'}
            print("   [FAIL] Missing API key")
            return
        
        try:
            client = get_openai_model()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Test message: respond with 'OK'"}],
                max_tokens=10
            )
            
            if response and response.choices:
                content = response.choices[0].message.content
                self.results['openai'] = {'status': 'working', 'error': None}
                print(f"   [OK] Working - Response: {content}")
            else:
                self.results['openai'] = {'status': 'failed', 'error': 'No response received'}
                print("   [FAIL] No response received")
                
        except Exception as e:
            self.results['openai'] = {'status': 'failed', 'error': str(e)}
            print(f"   [FAIL] Error: {str(e)}")
    
    def test_yfinance_api(self):
        """Test Yahoo Finance API connectivity"""
        print("[YFINANCE] Testing Yahoo Finance API...")
        
        try:
            # Test with a well-known ticker
            ticker = yf.Ticker("AAPL")
            info = ticker.info
            
            if info and 'longName' in info:
                self.results['yfinance'] = {'status': 'working', 'error': None}
                print(f"   [OK] Working - Retrieved: {info.get('longName', 'Unknown')}")
            else:
                self.results['yfinance'] = {'status': 'failed', 'error': 'No company info received'}
                print("   [FAIL] No company info received")
                
        except Exception as e:
            self.results['yfinance'] = {'status': 'failed', 'error': str(e)}
            print(f"   [FAIL] Error: {str(e)}")
    
    def test_serper_api(self):
        """Test Serper API connectivity"""
        print("[SERPER] Testing Serper API...")
        
        if not SERPER_API_KEY:
            self.results['serper'] = {'status': 'missing_key', 'error': 'SERPER_API_KEY not found in environment'}
            print("   [FAIL] Missing API key")
            return
        
        try:
            url = "https://google.serper.dev/search"
            payload = {
                'q': 'Apple Inc news',
                'num': 3,
                'gl': 'us',
                'hl': 'en'
            }
            headers = {
                'X-API-KEY': SERPER_API_KEY,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'organic' in data and data['organic']:
                    self.results['serper'] = {'status': 'working', 'error': None}
                    print(f"   [OK] Working - Found {len(data['organic'])} results")
                else:
                    self.results['serper'] = {'status': 'failed', 'error': 'No search results returned'}
                    print("   [FAIL] No search results returned")
            else:
                self.results['serper'] = {'status': 'failed', 'error': f'HTTP {response.status_code}: {response.text}'}
                print(f"   [FAIL] HTTP {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            self.results['serper'] = {'status': 'failed', 'error': str(e)}
            print(f"   [FAIL] Error: {str(e)}")
    
    def test_serpapi_api(self):
        """Test SerpAPI connectivity"""
        print("[SERPAPI] Testing SerpAPI...")
        
        if not SERPAPI_API_KEY:
            self.results['serpapi'] = {'status': 'missing_key', 'error': 'SERPAPI_API_KEY not found in environment'}
            print("   [FAIL] Missing API key")
            return
        
        try:
            # Simple requests-based test instead of serpapi package
            url = "https://serpapi.com/search"
            params = {
                "engine": "google",
                "q": "Apple Inc",
                "api_key": SERPAPI_API_KEY,
                "num": 3
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'organic_results' in data and data['organic_results']:
                    self.results['serpapi'] = {'status': 'working', 'error': None}
                    print(f"   [OK] Working - Found {len(data['organic_results'])} results")
                else:
                    self.results['serpapi'] = {'status': 'failed', 'error': 'No search results returned'}
                    print("   [FAIL] No search results returned")
            else:
                self.results['serpapi'] = {'status': 'failed', 'error': f'HTTP {response.status_code}'}
                print(f"   [FAIL] HTTP {response.status_code}")
                
        except Exception as e:
            self.results['serpapi'] = {'status': 'failed', 'error': str(e)}
            print(f"   [FAIL] Error: {str(e)}")
    
    def test_twitter_api(self):
        """Test Twitter API connectivity"""
        print("[TWITTER] Testing Twitter API...")
        
        twitter_token = os.environ.get('TWITTER_BEARER_TOKEN')
        twitter_api_key = os.environ.get('TWITTER_API_KEY')
        twitter_api_secret = os.environ.get('TWITTER_API_SECRET')
        
        # If no bearer token but have API key/secret, try to generate bearer token
        if not twitter_token and twitter_api_key and twitter_api_secret:
            print("   [INFO] Attempting to generate bearer token from API credentials...")
            try:
                import base64
                
                # Create authorization header for bearer token generation
                credentials = f"{twitter_api_key}:{twitter_api_secret}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                
                # Request bearer token
                token_url = "https://api.twitter.com/oauth2/token"
                token_headers = {
                    "Authorization": f"Basic {encoded_credentials}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                token_data = "grant_type=client_credentials"
                
                token_response = requests.post(token_url, headers=token_headers, data=token_data, timeout=10)
                
                if token_response.status_code == 200:
                    token_data = token_response.json()
                    twitter_token = token_data.get('access_token')
                    print("   [OK] Generated bearer token successfully")
                else:
                    print(f"   [FAIL] Failed to generate bearer token: HTTP {token_response.status_code}")
                    self.results['twitter'] = {'status': 'failed', 'error': f'Bearer token generation failed: {token_response.text}'}
                    return
                    
            except Exception as e:
                print(f"   [FAIL] Bearer token generation error: {e}")
                self.results['twitter'] = {'status': 'failed', 'error': f'Bearer token generation error: {str(e)}'}
                return
        
        if not twitter_token:
            self.results['twitter'] = {'status': 'missing_key', 'error': 'No Twitter credentials found (optional)'}
            print("   [WARN] Missing API credentials (optional)")
            return
        
        try:
            # Simple requests-based test with minimal query for free tier
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {"Authorization": f"Bearer {twitter_token}"}
            params = {"query": "Apple", "max_results": 10}  # Start with small request
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    self.results['twitter'] = {'status': 'working', 'error': None}
                    print(f"   [OK] Working - Found {len(data['data'])} tweets")
                else:
                    # Check if it's a data issue or API limitation
                    if 'meta' in data:
                        self.results['twitter'] = {'status': 'working', 'error': None}
                        print("   [OK] API working but no tweets found for query")
                    else:
                        self.results['twitter'] = {'status': 'failed', 'error': 'No tweets returned'}
                        print("   [FAIL] No tweets returned")
            elif response.status_code == 429:
                # Rate limit exceeded
                self.results['twitter'] = {'status': 'rate_limited', 'error': 'Rate limit exceeded - free tier limit reached'}
                print("   [LIMIT] Rate limit exceeded - free tier monthly quota reached")
            elif response.status_code == 401:
                self.results['twitter'] = {'status': 'failed', 'error': 'Authentication failed - check API credentials'}
                print("   [FAIL] Authentication failed - check API credentials")
            elif response.status_code == 403:
                # Access forbidden - might need higher tier
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_detail = error_data.get('detail', 'Access forbidden')
                self.results['twitter'] = {'status': 'access_denied', 'error': f'Access denied: {error_detail}'}
                print(f"   [ACCESS] Access denied - might need paid tier: {error_detail}")
            else:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', response.text[:100])
                except:
                    error_detail = response.text[:100]
                
                self.results['twitter'] = {'status': 'failed', 'error': f'HTTP {response.status_code}: {error_detail}'}
                print(f"   [FAIL] HTTP {response.status_code}: {error_detail}")
                
        except Exception as e:
            self.results['twitter'] = {'status': 'failed', 'error': str(e)}
            print(f"   [FAIL] Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("="*60)
        print("API CONNECTIVITY TESTS")
        print("="*60)
        
        self.test_gemini_api()
        self.test_openai_api()
        self.test_yfinance_api()
        self.test_serper_api()
        self.test_serpapi_api()
        self.test_twitter_api()
        
        print("\n" + "="*60)
        print("API TEST RESULTS SUMMARY")
        print("="*60)
        
        working_count = 0
        total_count = 0
        
        for api_name, result in self.results.items():
            status = result['status']
            error = result['error']
            
            if status == 'working':
                print(f"[OK] {api_name.upper()}: Working")
                working_count += 1
            elif status == 'missing_key':
                print(f"[KEY] {api_name.upper()}: Missing API key")
                if 'optional' not in str(error):
                    total_count += 1
            elif status == 'failed':
                print(f"[FAIL] {api_name.upper()}: Failed - {error}")
                total_count += 1
            else:
                print(f"[WARN] {api_name.upper()}: Not tested")
                total_count += 1
            
            if status != 'missing_key' or 'optional' not in str(error):
                total_count += 1
        
        print(f"\nOverall Status: {working_count}/{total_count} APIs working")
        
        # Recommendations
        print("\nRECOMMENDATIONS:")
        
        if self.results['gemini']['status'] != 'working' and self.results['openai']['status'] != 'working':
            print("CRITICAL: No LLM APIs working. Add GEMINI_API_KEY or OPENAI_API_KEY")
        
        if self.results['yfinance']['status'] != 'working':
            print("CRITICAL: Yahoo Finance not working. Financial analysis will fail")
        
        if self.results['serper']['status'] != 'working' and self.results['serpapi']['status'] != 'working':
            print("WARNING: No search APIs working. Sentiment and CEO analysis will be limited")
        
        if self.results['twitter']['status'] == 'missing_key':
            print("INFO: Twitter API not configured. Add TWITTER_BEARER_TOKEN for social sentiment")
        
        print("\nAPI SOURCES:")
        print("- GEMINI_API_KEY: https://aistudio.google.com/app/apikey")
        print("- OPENAI_API_KEY: https://platform.openai.com/api-keys") 
        print("- SERPER_API_KEY: https://serper.dev/")
        print("- SERPAPI_API_KEY: https://serpapi.com/")
        print("- TWITTER_BEARER_TOKEN: https://developer.twitter.com/")
        
        return self.results


def main():
    """Main test runner"""
    tester = APITester()
    results = tester.run_all_tests()
    
    # Exit with error code if critical APIs are failing
    critical_failures = 0
    if results['gemini']['status'] not in ['working'] and results['openai']['status'] not in ['working']:
        critical_failures += 1
    if results['yfinance']['status'] != 'working':
        critical_failures += 1
    
    if critical_failures > 0:
        print(f"\n[FAIL] Test completed with {critical_failures} critical failures")
        sys.exit(1)
    else:
        print(f"\n[OK] All critical APIs working!")
        sys.exit(0)


if __name__ == "__main__":
    main()