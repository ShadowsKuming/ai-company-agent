import requests
from bs4 import BeautifulSoup
import yfinance as yf
from typing import Dict, Any, List
# from googlesearch import search  # Will fallback to SERP API
import time
from src.config import SERPAPI_API_KEY


class CEOAnalyzer:
    """Analyzes CEO personality, leadership style, and future impact potential"""
    
    def __init__(self):
        self.serp_api_key = SERPAPI_API_KEY
    
    def get_company_leadership(self, ticker: str) -> Dict[str, Any]:
        """Get basic company and CEO information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            leadership_info = {
                'company_name': info.get('longName', ticker),
                'ceo_name': info.get('ceo', 'N/A'),
                'executives': info.get('companyOfficers', []),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'employee_count': info.get('fullTimeEmployees', 'N/A')
            }
            
            return leadership_info
            
        except Exception as e:
            return {'error': f"Failed to get leadership info: {str(e)}"}
    
    def search_ceo_background(self, ceo_name: str, company_name: str) -> Dict[str, Any]:
        """Search for CEO background, education, and career history"""
        try:
            search_queries = [
                f"{ceo_name} CEO {company_name} biography education background",
                f"{ceo_name} {company_name} leadership style management approach",
                f"{ceo_name} technical background engineering experience",
                f"{ceo_name} {company_name} interviews quotes philosophy"
            ]
            
            ceo_background = {
                'education': [],
                'career_history': [],
                'technical_background': [],
                'leadership_style': [],
                'public_statements': []
            }
            
            for query in search_queries:
                try:
                    if self.serp_api_key:
                        search_results = self.search_with_serper(query)
                    else:
                        continue  # Skip if no search API available
                    
                    for result in search_results:
                        content = self.scrape_content(result.get('link', ''))
                        if content:
                            if 'education' in query:
                                ceo_background['education'].append(content[:500])
                            elif 'leadership style' in query:
                                ceo_background['leadership_style'].append(content[:500])
                            elif 'technical background' in query:
                                ceo_background['technical_background'].append(content[:500])
                            elif 'interviews' in query:
                                ceo_background['public_statements'].append(content[:500])
                except Exception as e:
                    print(f"Search error for query '{query}': {e}")
                    continue
            
            return ceo_background
            
        except Exception as e:
            return {'error': f"Failed to search CEO background: {str(e)}"}
    
    def search_with_serper(self, query: str) -> List[Dict[str, Any]]:
        """Search using Serper API"""
        try:
            url = "https://google.serper.dev/search"
            payload = {
                'q': query,
                'num': 5,
                'gl': 'us',
                'hl': 'en'
            }
            headers = {
                'X-API-KEY': self.serp_api_key,
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
            
            return text[:1000]  # Limit to first 1000 characters
            
        except Exception:
            return ""
    
    def analyze_leadership_impact(self, ceo_background: Dict[str, Any], company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how CEO leadership might impact company future"""
        try:
            leadership_analysis = {
                'technical_competency': 0,
                'leadership_effectiveness': 0,
                'innovation_focus': 0,
                'future_impact_score': 0,
                'strengths': [],
                'potential_risks': [],
                'leadership_summary': ""
            }
            
            # Analyze technical background
            tech_keywords = ['engineer', 'technical', 'computer science', 'technology', 'programming', 'software']
            tech_content = ' '.join(ceo_background.get('technical_background', [])).lower()
            tech_score = sum(1 for keyword in tech_keywords if keyword in tech_content)
            leadership_analysis['technical_competency'] = min(tech_score * 2, 10)
            
            # Analyze leadership style
            leadership_keywords = ['innovative', 'visionary', 'strategic', 'collaborative', 'decisive', 'transformative']
            leadership_content = ' '.join(ceo_background.get('leadership_style', [])).lower()
            leadership_score = sum(1 for keyword in leadership_keywords if keyword in leadership_content)
            leadership_analysis['leadership_effectiveness'] = min(leadership_score * 1.5, 10)
            
            # Innovation focus analysis
            innovation_keywords = ['innovation', 'research', 'development', 'future', 'ai', 'technology', 'disruption']
            all_content = ' '.join([
                ' '.join(ceo_background.get('leadership_style', [])),
                ' '.join(ceo_background.get('public_statements', []))
            ]).lower()
            innovation_score = sum(1 for keyword in innovation_keywords if keyword in all_content)
            leadership_analysis['innovation_focus'] = min(innovation_score * 1.2, 10)
            
            # Calculate overall future impact score
            leadership_analysis['future_impact_score'] = (
                leadership_analysis['technical_competency'] * 0.4 +
                leadership_analysis['leadership_effectiveness'] * 0.4 +
                leadership_analysis['innovation_focus'] * 0.2
            )
            
            # Determine strengths and risks
            if leadership_analysis['technical_competency'] >= 7:
                leadership_analysis['strengths'].append("Strong technical background")
            elif leadership_analysis['technical_competency'] <= 3:
                leadership_analysis['potential_risks'].append("Limited technical expertise")
            
            if leadership_analysis['innovation_focus'] >= 7:
                leadership_analysis['strengths'].append("High innovation focus")
            elif leadership_analysis['innovation_focus'] <= 3:
                leadership_analysis['potential_risks'].append("Low innovation emphasis")
            
            return leadership_analysis
            
        except Exception as e:
            return {'error': f"Failed to analyze leadership impact: {str(e)}"}
    
    def analyze_ceo_complete(self, ticker: str) -> Dict[str, Any]:
        """Complete CEO analysis including background and leadership impact"""
        try:
            # Get company and leadership info
            company_info = self.get_company_leadership(ticker)
            
            if 'error' in company_info:
                return company_info
            
            ceo_name = company_info.get('ceo_name')
            company_name = company_info.get('company_name')
            
            if ceo_name == 'N/A' or not ceo_name:
                return {
                    'ticker': ticker,
                    'company_info': company_info,
                    'ceo_background': {},
                    'leadership_analysis': {},
                    'error': 'CEO information not available'
                }
            
            # Search for CEO background
            ceo_background = self.search_ceo_background(ceo_name, company_name)
            
            # Analyze leadership impact
            leadership_analysis = self.analyze_leadership_impact(ceo_background, company_info)
            
            return {
                'ticker': ticker,
                'company_info': company_info,
                'ceo_background': ceo_background,
                'leadership_analysis': leadership_analysis,
                'analysis_summary': {
                    'ceo_name': ceo_name,
                    'company_name': company_name,
                    'future_impact_score': leadership_analysis.get('future_impact_score', 0),
                    'key_strengths': leadership_analysis.get('strengths', []),
                    'potential_risks': leadership_analysis.get('potential_risks', []),
                    'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
        except Exception as e:
            return {'error': f"Failed to complete CEO analysis: {str(e)}"}