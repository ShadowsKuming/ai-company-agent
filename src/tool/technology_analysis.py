import requests
from bs4 import BeautifulSoup
import yfinance as yf
from typing import Dict, Any, List
import time
# from googlesearch import search  # Will use SERP API instead
from src.config import SERPAPI_API_KEY, SERPER_API_KEY
import json


class TechnologyAnalyzer:
    """Analyzes company's technology assets, IP portfolio, and technical competitive advantages"""
    
    def __init__(self):
        self.serp_api_key = SERPAPI_API_KEY
        self.serper_api_key = SERPER_API_KEY
    
    def get_company_tech_info(self, ticker: str) -> Dict[str, Any]:
        """Get basic company technology information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            tech_info = {
                'company_name': info.get('longName', ticker),
                'ticker': ticker,
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'business_summary': info.get('longBusinessSummary', ''),
                'website': info.get('website', ''),
                'employee_count': info.get('fullTimeEmployees', 'N/A')
            }
            
            return tech_info
            
        except Exception as e:
            return {'error': f"Failed to get company tech info: {str(e)}"}
    
    def search_patent_information(self, company_name: str, ticker: str) -> Dict[str, Any]:
        """Search for patent and IP information"""
        try:
            patent_data = {
                'patent_count_estimates': [],
                'key_patent_areas': [],
                'recent_patents': [],
                'ip_strategy': [],
                'innovation_indicators': []
            }
            
            search_queries = [
                f"{company_name} patents intellectual property portfolio",
                f"{company_name} patent filings USPTO recent innovations",
                f"{company_name} technology IP strategy licensing",
                f"{company_name} R&D innovation patent applications"
            ]
            
            for query in search_queries:
                try:
                    if self.serper_api_key:
                        search_results = self.search_with_serper(query)
                    else:
                        search_results = list(search(query, num_results=5, stop=5, pause=2))
                        search_results = [{'link': url, 'title': '', 'snippet': ''} for url in search_results]
                    
                    for result in search_results[:3]:
                        content = self.scrape_content(result.get('link', ''))
                        if content:
                            if 'patent' in query.lower():
                                patent_data['recent_patents'].append({
                                    'source': result.get('link', ''),
                                    'content': content[:300],
                                    'title': result.get('title', '')[:100]
                                })
                            elif 'strategy' in query.lower():
                                patent_data['ip_strategy'].append(content[:300])
                            elif 'innovation' in query.lower():
                                patent_data['innovation_indicators'].append(content[:300])
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"Patent search error for '{query}': {e}")
                    continue
            
            return patent_data
            
        except Exception as e:
            return {'error': f"Failed to search patent information: {str(e)}"}
    
    def search_with_serper(self, query: str) -> List[Dict[str, Any]]:
        """Search using Serper API"""
        try:
            url = "https://google.serper.dev/search"
            payload = {
                'q': query,
                'num': 10,
                'gl': 'us',
                'hl': 'en'
            }
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            
            results = []
            for result in data.get('organic', []):
                results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'link': result.get('link', ''),
                    'source': result.get('source', '')
                })
            
            return results
            
        except Exception as e:
            print(f"Serper search error: {e}")
            return []
    
    def scrape_content(self, url: str) -> str:
        """Scrape content from a URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:800]  # Limit to first 800 characters
            
        except Exception:
            return ""
    
    def analyze_technology_stack(self, company_name: str, ticker: str, business_summary: str) -> Dict[str, Any]:
        """Analyze company's technology stack and capabilities"""
        try:
            tech_stack = {
                'core_technologies': [],
                'emerging_tech_adoption': [],
                'technology_moats': [],
                'tech_partnerships': [],
                'digital_transformation': []
            }
            
            search_queries = [
                f"{company_name} technology stack architecture platform",
                f"{company_name} artificial intelligence AI machine learning",
                f"{company_name} cloud computing infrastructure technology",
                f"{company_name} software development tools technology partnerships",
                f"{company_name} digital transformation technology initiatives"
            ]
            
            # Analyze business summary for tech keywords
            tech_keywords = {
                'ai_ml': ['artificial intelligence', 'machine learning', 'AI', 'ML', 'neural', 'deep learning'],
                'cloud': ['cloud', 'AWS', 'Azure', 'Google Cloud', 'SaaS', 'PaaS'],
                'mobile': ['mobile', 'iOS', 'Android', 'app', 'smartphone'],
                'web': ['web', 'internet', 'online', 'digital', 'platform'],
                'data': ['big data', 'analytics', 'data science', 'data mining', 'database'],
                'security': ['cybersecurity', 'security', 'encryption', 'privacy'],
                'blockchain': ['blockchain', 'cryptocurrency', 'bitcoin', 'ethereum'],
                'iot': ['IoT', 'Internet of Things', 'connected devices', 'sensors']
            }
            
            summary_lower = business_summary.lower()
            for category, keywords in tech_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in summary_lower:
                        tech_stack['core_technologies'].append({
                            'category': category,
                            'technology': keyword,
                            'context': 'business_summary'
                        })
            
            # Search for additional technology information
            for query in search_queries:
                try:
                    if self.serper_api_key:
                        search_results = self.search_with_serper(query)
                    else:
                        continue  # Skip if no search API available
                    
                    for result in search_results[:2]:
                        content = self.scrape_content(result.get('link', ''))
                        if content:
                            if 'AI' in query or 'artificial intelligence' in query:
                                tech_stack['emerging_tech_adoption'].append(content[:300])
                            elif 'partnership' in query:
                                tech_stack['tech_partnerships'].append(content[:300])
                            elif 'transformation' in query:
                                tech_stack['digital_transformation'].append(content[:300])
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Technology search error for '{query}': {e}")
                    continue
            
            return tech_stack
            
        except Exception as e:
            return {'error': f"Failed to analyze technology stack: {str(e)}"}
    
    def calculate_technology_score(self, patent_data: Dict[str, Any], tech_stack: Dict[str, Any], company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall technology competitiveness score"""
        try:
            tech_score = {
                'innovation_score': 0,
                'patent_strength': 0,
                'tech_adoption': 0,
                'competitive_moat': 0,
                'overall_tech_score': 0,
                'technology_strengths': [],
                'technology_risks': []
            }
            
            # Calculate innovation score based on patents and R&D focus
            patent_indicators = len(patent_data.get('recent_patents', []))
            innovation_indicators = len(patent_data.get('innovation_indicators', []))
            tech_score['innovation_score'] = min((patent_indicators + innovation_indicators) * 1.5, 10)
            
            # Calculate patent strength
            ip_strategy_items = len(patent_data.get('ip_strategy', []))
            patent_areas = len(patent_data.get('key_patent_areas', []))
            tech_score['patent_strength'] = min((ip_strategy_items + patent_areas) * 2, 10)
            
            # Calculate technology adoption score
            core_techs = len(tech_stack.get('core_technologies', []))
            emerging_tech = len(tech_stack.get('emerging_tech_adoption', []))
            tech_score['tech_adoption'] = min((core_techs + emerging_tech * 2) * 0.8, 10)
            
            # Calculate competitive moat
            partnerships = len(tech_stack.get('tech_partnerships', []))
            transformation = len(tech_stack.get('digital_transformation', []))
            tech_score['competitive_moat'] = min((partnerships + transformation) * 1.2, 10)
            
            # Calculate overall score
            weights = {
                'innovation': 0.3,
                'patents': 0.25,
                'adoption': 0.25,
                'moat': 0.2
            }
            
            tech_score['overall_tech_score'] = (
                tech_score['innovation_score'] * weights['innovation'] +
                tech_score['patent_strength'] * weights['patents'] +
                tech_score['tech_adoption'] * weights['adoption'] +
                tech_score['competitive_moat'] * weights['moat']
            )
            
            # Determine strengths and risks
            if tech_score['innovation_score'] >= 7:
                tech_score['technology_strengths'].append("Strong innovation pipeline")
            elif tech_score['innovation_score'] <= 3:
                tech_score['technology_risks'].append("Limited innovation indicators")
            
            if tech_score['patent_strength'] >= 7:
                tech_score['technology_strengths'].append("Robust IP portfolio")
            elif tech_score['patent_strength'] <= 3:
                tech_score['technology_risks'].append("Weak intellectual property protection")
            
            if tech_score['tech_adoption'] >= 7:
                tech_score['technology_strengths'].append("Advanced technology adoption")
            elif tech_score['tech_adoption'] <= 3:
                tech_score['technology_risks'].append("Limited technology modernization")
            
            return tech_score
            
        except Exception as e:
            return {'error': f"Failed to calculate technology score: {str(e)}"}
    
    def analyze_technology_complete(self, ticker: str) -> Dict[str, Any]:
        """Complete technology analysis including patents, stack, and competitive position"""
        try:
            # Get company information
            company_info = self.get_company_tech_info(ticker)
            
            if 'error' in company_info:
                return company_info
            
            company_name = company_info['company_name']
            business_summary = company_info.get('business_summary', '')
            
            # Search patent and IP information
            patent_data = self.search_patent_information(company_name, ticker)
            
            # Analyze technology stack
            tech_stack = self.analyze_technology_stack(company_name, ticker, business_summary)
            
            # Calculate technology scores
            tech_scores = self.calculate_technology_score(patent_data, tech_stack, company_info)
            
            return {
                'ticker': ticker,
                'company_info': company_info,
                'patent_analysis': patent_data,
                'technology_stack': tech_stack,
                'technology_scores': tech_scores,
                'analysis_summary': {
                    'company_name': company_name,
                    'overall_tech_score': tech_scores.get('overall_tech_score', 0),
                    'key_strengths': tech_scores.get('technology_strengths', []),
                    'potential_risks': tech_scores.get('technology_risks', []),
                    'sector': company_info.get('sector', 'N/A'),
                    'technology_focus_areas': [tech['category'] for tech in tech_stack.get('core_technologies', [])],
                    'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
        except Exception as e:
            return {'error': f"Failed to complete technology analysis: {str(e)}"}