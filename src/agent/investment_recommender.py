import json
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path

from src.config import default_llm, llm_type, get_gemini_model, get_openai_model


class InvestmentRecommenderAgent:
    """Agent that analyzes ticker analysis results and provides investment recommendations"""
    
    def __init__(self, use_llm: str = "gemini"):
        """Initialize the investment recommender agent
        
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
        
        print(f"✅ Investment Recommender Agent initialized with {self.llm_type.upper()} LLM")
    
    def load_ticker_analysis(self, ticker: str) -> Dict[str, Any]:
        """Load the latest analysis results for a ticker"""
        try:
            reports_dir = Path(f"reports/{ticker.upper()}/raw_data")
            
            if not reports_dir.exists():
                return {'error': f"No analysis data found for {ticker}"}
            
            # Find the latest analysis files
            analysis_files = list(reports_dir.glob("*.json"))
            if not analysis_files:
                return {'error': f"No analysis files found for {ticker}"}
            
            # Load all analysis data
            analysis_data = {
                'ticker': ticker.upper(),
                'loaded_files': []
            }
            
            for file_path in analysis_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Determine analysis type from filename
                    filename = file_path.stem
                    if 'cash_flow' in filename or 'financial' in filename:
                        analysis_data['financial_analysis'] = data
                    elif 'ceo' in filename or 'leadership' in filename:
                        analysis_data['ceo_analysis'] = data
                    elif 'technology' in filename:
                        analysis_data['technology_analysis'] = data
                    elif 'sentiment' in filename:
                        analysis_data['sentiment_analysis'] = data
                    elif 'profit' in filename:
                        analysis_data['profit_analysis'] = data
                    
                    analysis_data['loaded_files'].append(str(file_path))
                    
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
            
            return analysis_data
            
        except Exception as e:
            return {'error': f"Failed to load analysis for {ticker}: {str(e)}"}
    
    def calculate_investment_metrics(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed investment metrics from analysis data"""
        metrics = {
            'growth_potential': 0,
            'financial_stability': 0,
            'leadership_quality': 0,
            'innovation_capacity': 0,
            'market_sentiment': 0,
            'risk_factors': [],
            'opportunity_factors': [],
            'time_horizon_suitability': {},
            'investment_style_fit': {}
        }
        
        # Growth Potential (based on R&D, revenue trends, technology)
        growth_score = 0
        
        # From financial analysis
        financial_data = analysis_data.get('financial_analysis', {})
        if 'analysis_summary' in financial_data:
            future_focus = financial_data['analysis_summary'].get('future_focus_score', 0)
            growth_score += future_focus * 0.4
        
        # From technology analysis
        tech_data = analysis_data.get('technology_analysis', {})
        if 'analysis_summary' in tech_data:
            tech_score = tech_data['analysis_summary'].get('overall_tech_score', 0)
            growth_score += tech_score * 0.6
        
        metrics['growth_potential'] = min(growth_score, 10)
        
        # Financial Stability
        stability_score = 5  # baseline
        
        profit_data = analysis_data.get('profit_analysis', {})
        if 'company_metrics' in profit_data:
            roe = profit_data['company_metrics'].get('roe')
            profit_margins = profit_data['company_metrics'].get('profit_margins_current', {})
            
            if roe and roe > 0.15:
                stability_score += 2
            elif roe and roe < 0.05:
                stability_score -= 1
            
            profit_margin = profit_margins.get('profit_margin')
            if profit_margin and profit_margin > 0.1:
                stability_score += 2
            elif profit_margin and profit_margin < 0.02:
                stability_score -= 1
        
        metrics['financial_stability'] = max(min(stability_score, 10), 0)
        
        # Leadership Quality
        ceo_data = analysis_data.get('ceo_analysis', {})
        if 'analysis_summary' in ceo_data:
            leadership_score = ceo_data['analysis_summary'].get('future_impact_score', 0)
            metrics['leadership_quality'] = leadership_score
        
        # Innovation Capacity
        metrics['innovation_capacity'] = metrics['growth_potential']  # Same as growth for now
        
        # Market Sentiment
        sentiment_data = analysis_data.get('sentiment_analysis', {})
        if 'analysis_summary' in sentiment_data:
            sentiment_score = sentiment_data['analysis_summary'].get('overall_sentiment_score', 0)
            # Convert from -1 to 1 range to 0-10 range
            metrics['market_sentiment'] = (sentiment_score + 1) * 5
        
        # Risk Factors Analysis
        if metrics['financial_stability'] < 5:
            metrics['risk_factors'].append("Low financial stability indicators")
        
        if metrics['leadership_quality'] < 5:
            metrics['risk_factors'].append("Questionable leadership effectiveness")
        
        if metrics['market_sentiment'] < 4:
            metrics['risk_factors'].append("Negative market sentiment")
        
        if tech_data.get('analysis_summary', {}).get('potential_risks'):
            metrics['risk_factors'].extend(tech_data['analysis_summary']['potential_risks'][:2])
        
        # Opportunity Factors
        if metrics['growth_potential'] > 7:
            metrics['opportunity_factors'].append("Strong growth potential")
        
        if metrics['innovation_capacity'] > 7:
            metrics['opportunity_factors'].append("High innovation capacity")
        
        if metrics['market_sentiment'] > 6:
            metrics['opportunity_factors'].append("Positive market sentiment")
        
        if tech_data.get('analysis_summary', {}).get('key_strengths'):
            metrics['opportunity_factors'].extend(tech_data['analysis_summary']['key_strengths'][:2])
        
        # Time Horizon Suitability
        avg_score = (metrics['growth_potential'] + metrics['financial_stability'] + 
                    metrics['leadership_quality'] + metrics['innovation_capacity']) / 4
        
        if metrics['growth_potential'] > 7 and metrics['innovation_capacity'] > 7:
            metrics['time_horizon_suitability']['long_term'] = 'excellent'
            metrics['time_horizon_suitability']['medium_term'] = 'good'
            metrics['time_horizon_suitability']['short_term'] = 'moderate'
        elif avg_score > 6:
            metrics['time_horizon_suitability']['long_term'] = 'good'
            metrics['time_horizon_suitability']['medium_term'] = 'good'
            metrics['time_horizon_suitability']['short_term'] = 'moderate'
        else:
            metrics['time_horizon_suitability']['long_term'] = 'moderate'
            metrics['time_horizon_suitability']['medium_term'] = 'moderate'
            metrics['time_horizon_suitability']['short_term'] = 'poor'
        
        # Investment Style Fit
        if metrics['growth_potential'] > 7:
            metrics['investment_style_fit']['growth'] = 'excellent'
        elif metrics['growth_potential'] > 5:
            metrics['investment_style_fit']['growth'] = 'good'
        else:
            metrics['investment_style_fit']['growth'] = 'poor'
        
        if metrics['financial_stability'] > 7 and metrics['market_sentiment'] > 5:
            metrics['investment_style_fit']['value'] = 'good'
        else:
            metrics['investment_style_fit']['value'] = 'moderate'
        
        if metrics['innovation_capacity'] > 8:
            metrics['investment_style_fit']['innovation'] = 'excellent'
        elif metrics['innovation_capacity'] > 6:
            metrics['investment_style_fit']['innovation'] = 'good'
        else:
            metrics['investment_style_fit']['innovation'] = 'moderate'
        
        return metrics
    
    def generate_recommendation(self, ticker: str, investment_metrics: Dict[str, Any], analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive investment recommendation"""
        
        # Calculate overall investment score
        weights = {
            'growth_potential': 0.25,
            'financial_stability': 0.25,
            'leadership_quality': 0.15,
            'innovation_capacity': 0.20,
            'market_sentiment': 0.15
        }
        
        overall_score = sum(
            investment_metrics[key] * weight 
            for key, weight in weights.items()
        )
        
        # Determine recommendation category
        if overall_score >= 8:
            recommendation = "STRONG BUY"
            confidence = "High"
        elif overall_score >= 6.5:
            recommendation = "BUY"
            confidence = "Medium-High"
        elif overall_score >= 5:
            recommendation = "HOLD"
            confidence = "Medium"
        elif overall_score >= 3.5:
            recommendation = "WEAK HOLD"
            confidence = "Medium-Low"
        else:
            recommendation = "SELL"
            confidence = "High"
        
        # Generate LLM-powered detailed reasoning
        reasoning = self.generate_llm_reasoning(ticker, investment_metrics, analysis_data, recommendation)
        
        recommendation_result = {
            'ticker': ticker,
            'recommendation': recommendation,
            'overall_score': round(overall_score, 2),
            'confidence_level': confidence,
            'detailed_scores': {
                'growth_potential': investment_metrics['growth_potential'],
                'financial_stability': investment_metrics['financial_stability'],
                'leadership_quality': investment_metrics['leadership_quality'],
                'innovation_capacity': investment_metrics['innovation_capacity'],
                'market_sentiment': investment_metrics['market_sentiment']
            },
            'time_horizon_recommendations': investment_metrics['time_horizon_suitability'],
            'investment_style_fit': investment_metrics['investment_style_fit'],
            'key_risks': investment_metrics['risk_factors'][:5],
            'key_opportunities': investment_metrics['opportunity_factors'][:5],
            'llm_reasoning': reasoning,
            'recommendation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analyst': f"AI Investment Recommender ({self.llm_type.upper()})"
        }
        
        return recommendation_result
    
    def generate_llm_reasoning(self, ticker: str, metrics: Dict[str, Any], analysis_data: Dict[str, Any], recommendation: str) -> str:
        """Generate detailed reasoning using LLM"""
        try:
            prompt = f"""
            As an expert financial analyst, provide detailed reasoning for the {recommendation} recommendation for {ticker}.
            
            Consider these key metrics:
            - Growth Potential: {metrics['growth_potential']}/10
            - Financial Stability: {metrics['financial_stability']}/10
            - Leadership Quality: {metrics['leadership_quality']}/10
            - Innovation Capacity: {metrics['innovation_capacity']}/10
            - Market Sentiment: {metrics['market_sentiment']}/10
            
            Key Risks: {', '.join(metrics['risk_factors'][:3])}
            Key Opportunities: {', '.join(metrics['opportunity_factors'][:3])}
            
            Provide a comprehensive analysis covering:
            1. Primary reasons supporting this recommendation
            2. Key risk factors to monitor
            3. Catalysts that could change the outlook
            4. Ideal holding period and investment approach
            
            Keep the analysis professional, specific, and actionable. Limit to 400 words.
            """
            
            if self.llm_type == "gemini":
                response = self.llm.generate_content(prompt)
                return response.text
            else:  # OpenAI
                response = self.llm.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert financial analyst providing investment recommendations."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=600
                )
                return response.choices[0].message.content
                
        except Exception as e:
            return f"Detailed reasoning generation failed: {str(e)}. Based on the quantitative analysis, this {recommendation} recommendation is supported by the overall score and individual metric assessments."
    
    def save_recommendation(self, ticker: str, recommendation: Dict[str, Any]) -> str:
        """Save recommendation to ticker folder"""
        try:
            reports_dir = Path(f"reports/{ticker.upper()}")
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"investment_recommendation_{timestamp}.json"
            filepath = reports_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(recommendation, f, indent=2, default=str)
            
            # Also create a markdown summary
            md_filename = f"investment_recommendation_{timestamp}.md"
            md_filepath = reports_dir / md_filename
            
            md_content = self.create_recommendation_markdown(recommendation)
            
            with open(md_filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            return str(md_filepath)
            
        except Exception as e:
            return f"Failed to save recommendation: {str(e)}"
    
    def create_recommendation_markdown(self, recommendation: Dict[str, Any]) -> str:
        """Create markdown report for recommendation"""
        
        ticker = recommendation['ticker']
        rec = recommendation['recommendation']
        score = recommendation['overall_score']
        confidence = recommendation['confidence_level']
        
        content = f"""# Investment Recommendation: {ticker}

**Recommendation:** {rec}  
**Overall Score:** {score}/10  
**Confidence Level:** {confidence}  
**Analysis Date:** {recommendation['recommendation_date']}  
**Analyst:** {recommendation['analyst']}

---

## Executive Summary

Based on comprehensive analysis across five key dimensions, {ticker} receives a **{rec}** recommendation with an overall score of **{score}/10**.

---

## Detailed Scoring

| Metric | Score | Rating |
|--------|-------|--------|
| Growth Potential | {recommendation['detailed_scores']['growth_potential']}/10 | {'Excellent' if recommendation['detailed_scores']['growth_potential'] >= 8 else 'Good' if recommendation['detailed_scores']['growth_potential'] >= 6 else 'Moderate'} |
| Financial Stability | {recommendation['detailed_scores']['financial_stability']}/10 | {'Excellent' if recommendation['detailed_scores']['financial_stability'] >= 8 else 'Good' if recommendation['detailed_scores']['financial_stability'] >= 6 else 'Moderate'} |
| Leadership Quality | {recommendation['detailed_scores']['leadership_quality']}/10 | {'Excellent' if recommendation['detailed_scores']['leadership_quality'] >= 8 else 'Good' if recommendation['detailed_scores']['leadership_quality'] >= 6 else 'Moderate'} |
| Innovation Capacity | {recommendation['detailed_scores']['innovation_capacity']}/10 | {'Excellent' if recommendation['detailed_scores']['innovation_capacity'] >= 8 else 'Good' if recommendation['detailed_scores']['innovation_capacity'] >= 6 else 'Moderate'} |
| Market Sentiment | {recommendation['detailed_scores']['market_sentiment']}/10 | {'Positive' if recommendation['detailed_scores']['market_sentiment'] >= 6 else 'Neutral' if recommendation['detailed_scores']['market_sentiment'] >= 4 else 'Negative'} |

---

## Investment Horizon Recommendations

- **Long-term (3+ years):** {recommendation['time_horizon_recommendations'].get('long_term', 'N/A').title()}
- **Medium-term (1-3 years):** {recommendation['time_horizon_recommendations'].get('medium_term', 'N/A').title()}
- **Short-term (<1 year):** {recommendation['time_horizon_recommendations'].get('short_term', 'N/A').title()}

---

## Investment Style Fit

- **Growth Investing:** {recommendation['investment_style_fit'].get('growth', 'N/A').title()}
- **Value Investing:** {recommendation['investment_style_fit'].get('value', 'N/A').title()}
- **Innovation Focus:** {recommendation['investment_style_fit'].get('innovation', 'N/A').title()}

---

## Key Opportunities

{chr(10).join(f"- {opportunity}" for opportunity in recommendation['key_opportunities'])}

---

## Key Risks

{chr(10).join(f"- {risk}" for risk in recommendation['key_risks'])}

---

## Detailed Analysis

{recommendation['llm_reasoning']}

---

## Disclaimer

This analysis is generated by an AI system for informational purposes only and should not be considered as personalized investment advice. Always conduct your own research and consult with qualified financial advisors before making investment decisions.

---

*Report generated by AI Investment Recommender Agent*
"""
        
        return content
    
    def recommend_investment(self, ticker: str) -> Dict[str, Any]:
        """Main method to generate investment recommendation for a ticker"""
        
        print(f"\n💡 Generating investment recommendation for {ticker.upper()}")
        print("=" * 60)
        
        # Load analysis data
        print("📁 Loading analysis data...")
        analysis_data = self.load_ticker_analysis(ticker)
        
        if 'error' in analysis_data:
            return analysis_data
        
        print(f"   ✅ Loaded {len(analysis_data.get('loaded_files', []))} analysis files")
        
        # Calculate investment metrics
        print("📊 Calculating investment metrics...")
        investment_metrics = self.calculate_investment_metrics(analysis_data)
        print("   ✅ Investment metrics calculated")
        
        # Generate recommendation
        print("🎯 Generating recommendation...")
        recommendation = self.generate_recommendation(ticker, investment_metrics, analysis_data)
        print(f"   ✅ Recommendation: {recommendation['recommendation']}")
        
        # Save recommendation
        print("💾 Saving recommendation...")
        report_path = self.save_recommendation(ticker, recommendation)
        recommendation['report_path'] = report_path
        print(f"   ✅ Recommendation saved: {report_path}")
        
        print("\n" + "=" * 60)
        print(f"🎯 Investment Recommendation: {recommendation['recommendation']}")
        print(f"📊 Overall Score: {recommendation['overall_score']}/10")
        print(f"🔍 Confidence: {recommendation['confidence_level']}")
        print(f"📁 Report saved: {report_path}")
        
        return recommendation


# Convenience function
def get_investment_recommendation(ticker: str, use_llm: str = "gemini") -> Dict[str, Any]:
    """Convenience function to get investment recommendation
    
    Args:
        ticker: Stock ticker symbol
        use_llm: "gemini" for Gemini Pro or "openai" for ChatGPT-4o
    
    Returns:
        Investment recommendation results
    """
    agent = InvestmentRecommenderAgent(use_llm=use_llm)
    return agent.recommend_investment(ticker)