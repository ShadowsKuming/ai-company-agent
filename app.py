import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import time

# Add current directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our agents
from src.agent.ticker_analyzer import TickerAnalyzerAgent, analyze_ticker
from src.agent.investment_recommender import InvestmentRecommenderAgent, get_investment_recommendation

app = typer.Typer(help="🚀 AI-Powered Ticker Analyzer & Investment Recommender")
console = Console()


@app.command("analyze")
def analyze_company(
    company: str = typer.Argument(..., help="Company ticker symbol (e.g., AAPL) or company name"),
    llm: str = typer.Option("gemini", "--llm", "-l", help="LLM to use: 'gemini' or 'openai'"),
    recommend: bool = typer.Option(True, "--recommend/--no-recommend", "-r/-nr", help="Generate investment recommendation after analysis"),
    force_new: bool = typer.Option(False, "--force-new/--use-cache", "-f", help="Force new analysis even if recent analysis exists")
):
    """
    🎯 Run comprehensive analysis on a company ticker
    
    Analyzes 5 key aspects:
    1. Cash flow analysis (revenue streams + R&D ratio)
    2. Profit mechanism analysis  
    3. CEO personality & leadership analysis
    4. Technology & IP analysis
    5. Market sentiment analysis (news + Twitter)
    """
    
    # Convert company name to ticker if needed (simple heuristic)
    ticker = company.upper()
    if len(ticker) > 5:
        console.print(f"[yellow]WARNING: '{company}' looks like a company name. Please use the ticker symbol instead (e.g., AAPL for Apple).[/yellow]")
        return
    
    console.print(Panel(
        f"[bold green]Starting Analysis for {ticker}[/bold green]\n"
        f"[cyan]LLM: {llm.upper()}[/cyan]\n"
        f"[cyan]Investment Recommendation: {'Yes' if recommend else 'No'}[/cyan]\n"
        f"[cyan]Cache Strategy: {'Force New' if force_new else 'Use Cache (15 days)'}[/cyan]",
        title="AI Ticker Analyzer",
        border_style="green"
    ))
    
    try:
        # Run comprehensive analysis
        start_time = time.time()
        
        with console.status(f"[bold green]Analyzing {ticker} (RAG + Workflow Enhanced)..."):
            # Create analyzer instance for enhanced features
            analyzer = TickerAnalyzerAgent(use_llm=llm)
            
            # Run enhanced analysis with RAG and workflow
            analysis_result = analyzer.analyze_ticker_comprehensive(
                ticker, 
                force_new=force_new,
                use_workflow=True,  # Enable LangGraph workflow
                use_rag=True        # Enable RAG enhancement
            )
        
        analysis_time = time.time() - start_time
        
        # Display results summary
        if 'error' not in analysis_result:
            overall_scores = analysis_result.get('overall_scores', {})
            is_cached = analysis_result.get('is_cached', False)
            
            console.print("\n" + "="*60)
            if is_cached:
                cache_age = analysis_result.get('cache_age_days', 0)
                console.print(f"[bold blue]Using Cached Analysis for {ticker}[/bold blue]")
                console.print(f"[dim]Cache age: {cache_age} days old[/dim]")
            else:
                console.print(f"[bold green]Analysis Complete for {ticker}[/bold green]")
                console.print(f"[dim]Analysis time: {analysis_time:.1f} seconds[/dim]")
            
            # Display key scores
            if overall_scores:
                console.print("\n[bold]📊 Key Scores:[/bold]")
                console.print(f"  🔬 Future Focus (R&D): [cyan]{overall_scores.get('future_focus_score', 'N/A')}/10[/cyan]")
                console.print(f"  👤 Leadership Impact: [cyan]{overall_scores.get('leadership_score', 'N/A')}/10[/cyan]")
                console.print(f"  💻 Technology Score: [cyan]{overall_scores.get('technology_score', 'N/A')}/10[/cyan]")
                console.print(f"  💰 Financial Health: [cyan]{overall_scores.get('financial_health_score', 'N/A')}/10[/cyan]")
                console.print(f"  📈 Market Sentiment: [cyan]{overall_scores.get('sentiment_score', 'N/A'):.1f}/10[/cyan]")
                console.print(f"  🎯 Overall Investment Score: [bold cyan]{overall_scores.get('overall_investment_score', 'N/A')}/10[/bold cyan]")
                console.print(f"  ⚠️  Risk Level: [{'red' if overall_scores.get('risk_level') == 'high' else 'yellow' if overall_scores.get('risk_level') == 'medium' else 'green'}]{overall_scores.get('risk_level', 'N/A').upper()}[/]")
            
            # Display file locations
            report_files = analysis_result.get('report_files', {})
            if 'report_file' in report_files:
                console.print(f"\n[bold]Reports saved to:[/bold]")
                console.print(f"  Full Report: [green]{report_files['report_file']}[/green]")
                console.print(f"  Data Folder: [green]{report_files.get('ticker_folder', 'N/A')}[/green]")
            
        else:
            error_msg = analysis_result['error']
            console.print(f"[red]ERROR: Analysis failed: {error_msg}[/red]")
            
            # Provide helpful suggestions for common errors
            if 'Invalid ticker' in error_msg or 'no company information found' in error_msg:
                console.print(f"[yellow]SUGGESTION: Make sure '{ticker}' is a valid stock ticker symbol (e.g., AAPL for Apple, GOOGL for Google)[/yellow]")
            elif 'No financial data available' in error_msg:
                console.print(f"[yellow]SUGGESTION: This ticker may be valid but lacks financial data. Try a larger public company.[/yellow]")
            
            return
        
        # Generate investment recommendation if requested
        if recommend:
            console.print("\n" + "="*60)
            console.print("[bold yellow]💡 Generating Investment Recommendation...[/bold yellow]")
            
            try:
                with console.status(f"[bold yellow]Analyzing investment potential for {ticker}..."):
                    recommendation = get_investment_recommendation(ticker, use_llm=llm)
                
                if 'error' not in recommendation:
                    rec_text = recommendation['recommendation']
                    score = recommendation['overall_score']
                    confidence = recommendation['confidence_level']
                    
                    # Color code the recommendation
                    if 'BUY' in rec_text:
                        rec_color = 'green'
                    elif 'HOLD' in rec_text:
                        rec_color = 'yellow'
                    else:
                        rec_color = 'red'
                    
                    console.print(Panel(
                        f"[bold {rec_color}]{rec_text}[/bold {rec_color}]\n"
                        f"[cyan]Score: {score}/10[/cyan]\n"
                        f"[cyan]Confidence: {confidence}[/cyan]",
                        title=f"🎯 Investment Recommendation for {ticker}",
                        border_style=rec_color
                    ))
                    
                    # Show key points
                    if recommendation.get('key_opportunities'):
                        console.print("\n[bold green]🚀 Key Opportunities:[/bold green]")
                        for opp in recommendation['key_opportunities'][:3]:
                            console.print(f"  • {opp}")
                    
                    if recommendation.get('key_risks'):
                        console.print("\n[bold red]⚠️  Key Risks:[/bold red]")
                        for risk in recommendation['key_risks'][:3]:
                            console.print(f"  • {risk}")
                    
                    console.print(f"\n[bold]📄 Recommendation report:[/bold] [green]{recommendation.get('report_path', 'N/A')}[/green]")
                
                else:
                    console.print(f"[red]❌ Recommendation failed: {recommendation['error']}[/red]")
            
            except Exception as e:
                console.print(f"[red]❌ Recommendation generation failed: {str(e)}[/red]")
        
        console.print("\n" + "="*60)
        console.print("[bold green]🎉 Analysis Complete![/bold green]")
        
    except Exception as e:
        console.print(f"[red]❌ Analysis failed with error: {str(e)}[/red]")


@app.command("recommend")
def recommend_only(
    ticker: str = typer.Argument(..., help="Company ticker symbol (e.g., AAPL)"),
    llm: str = typer.Option("gemini", "--llm", "-l", help="LLM to use: 'gemini' or 'openai'")
):
    """
    💡 Generate investment recommendation for a previously analyzed ticker
    
    Requires that you've already run 'analyze' command for this ticker.
    """
    
    ticker = ticker.upper()
    
    console.print(Panel(
        f"[bold yellow]💡 Generating Investment Recommendation for {ticker}[/bold yellow]\n"
        f"[cyan]LLM: {llm.upper()}[/cyan]",
        title="Investment Recommender",
        border_style="yellow"
    ))
    
    try:
        with console.status(f"[bold yellow]Analyzing investment potential for {ticker}..."):
            recommendation = get_investment_recommendation(ticker, use_llm=llm)
        
        if 'error' not in recommendation:
            rec_text = recommendation['recommendation']
            score = recommendation['overall_score']
            confidence = recommendation['confidence_level']
            
            # Color code the recommendation
            if 'BUY' in rec_text:
                rec_color = 'green'
            elif 'HOLD' in rec_text:
                rec_color = 'yellow'
            else:
                rec_color = 'red'
            
            console.print(Panel(
                f"[bold {rec_color}]{rec_text}[/bold {rec_color}]\n"
                f"[cyan]Score: {score}/10[/cyan]\n"
                f"[cyan]Confidence: {confidence}[/cyan]",
                title=f"🎯 Investment Recommendation for {ticker}",
                border_style=rec_color
            ))
            
            # Show detailed scores
            detailed = recommendation.get('detailed_scores', {})
            if detailed:
                console.print("\n[bold]📊 Detailed Scores:[/bold]")
                console.print(f"  🔬 Growth Potential: [cyan]{detailed.get('growth_potential', 'N/A')}/10[/cyan]")
                console.print(f"  💰 Financial Stability: [cyan]{detailed.get('financial_stability', 'N/A')}/10[/cyan]")
                console.print(f"  👤 Leadership Quality: [cyan]{detailed.get('leadership_quality', 'N/A')}/10[/cyan]")
                console.print(f"  💻 Innovation Capacity: [cyan]{detailed.get('innovation_capacity', 'N/A')}/10[/cyan]")
                console.print(f"  📈 Market Sentiment: [cyan]{detailed.get('market_sentiment', 'N/A'):.1f}/10[/cyan]")
            
            # Show time horizon recommendations
            time_horizon = recommendation.get('time_horizon_recommendations', {})
            if time_horizon:
                console.print("\n[bold]⏰ Time Horizon Fit:[/bold]")
                console.print(f"  📅 Long-term (3+ years): [cyan]{time_horizon.get('long_term', 'N/A').title()}[/cyan]")
                console.print(f"  📅 Medium-term (1-3 years): [cyan]{time_horizon.get('medium_term', 'N/A').title()}[/cyan]")
                console.print(f"  📅 Short-term (<1 year): [cyan]{time_horizon.get('short_term', 'N/A').title()}[/cyan]")
            
            # Show investment style fit
            style_fit = recommendation.get('investment_style_fit', {})
            if style_fit:
                console.print("\n[bold]🎨 Investment Style Fit:[/bold]")
                console.print(f"  📈 Growth Investing: [cyan]{style_fit.get('growth', 'N/A').title()}[/cyan]")
                console.print(f"  💎 Value Investing: [cyan]{style_fit.get('value', 'N/A').title()}[/cyan]")
                console.print(f"  🚀 Innovation Focus: [cyan]{style_fit.get('innovation', 'N/A').title()}[/cyan]")
            
            console.print(f"\n[bold]📄 Full recommendation report:[/bold] [green]{recommendation.get('report_path', 'N/A')}[/green]")
        
        else:
            console.print(f"[red]❌ Recommendation failed: {recommendation['error']}[/red]")
            console.print("[yellow]💡 Tip: Make sure you've run the 'analyze' command first for this ticker.[/yellow]")
    
    except Exception as e:
        console.print(f"[red]❌ Recommendation generation failed: {str(e)}[/red]")


@app.command("status")
def check_status(
    ticker: str = typer.Argument(..., help="Company ticker symbol to check")
):
    """
    📋 Check analysis status and view summary for a ticker
    """
    
    ticker = ticker.upper()
    
    try:
        from src.agent.ticker_analyzer import TickerAnalyzerAgent
        agent = TickerAnalyzerAgent()
        summary = agent.get_analysis_summary(ticker)
        
        console.print(Panel(
            summary,
            title=f"📋 Analysis Status for {ticker}",
            border_style="blue"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Status check failed: {str(e)}[/red]")


@app.command("config")
def show_config():
    """
    ⚙️  Show current configuration and API status
    """
    
    try:
        from src.config import GEMINI_API_KEY, OPENAI_API_KEY, SERPAPI_API_KEY, SERPER_API_KEY
        
        config_text = "[bold]🔧 Current Configuration:[/bold]\n\n"
        
        # API Keys status
        config_text += "[bold]API Keys:[/bold]\n"
        config_text += f"  🤖 Gemini API: [{'green' if GEMINI_API_KEY else 'red'}]{'Configured' if GEMINI_API_KEY else 'Missing'}[/]\n"
        config_text += f"  🤖 OpenAI API: [{'green' if OPENAI_API_KEY else 'red'}]{'Configured' if OPENAI_API_KEY else 'Missing'}[/]\n"
        config_text += f"  🔍 SERP API: [{'green' if SERPAPI_API_KEY else 'red'}]{'Configured' if SERPAPI_API_KEY else 'Missing'}[/]\n"
        config_text += f"  🔍 Serper API: [{'green' if SERPER_API_KEY else 'red'}]{'Configured' if SERPER_API_KEY else 'Missing'}[/]\n"
        
        # Twitter API
        import os
        twitter_key = os.environ.get('TWITTER_BEARER_TOKEN')
        config_text += f"  🐦 Twitter API: [{'green' if twitter_key else 'yellow'}]{'Configured' if twitter_key else 'Optional - Add TWITTER_BEARER_TOKEN for Twitter sentiment'}[/]\n"
        
        config_text += "\n[bold]Analysis Capabilities:[/bold]\n"
        config_text += "  📊 Cash Flow Analysis: [green]✅ Enabled[/green]\n"
        config_text += "  💰 Profit Analysis: [green]✅ Enabled[/green]\n"
        config_text += "  👤 CEO Analysis: [green]✅ Enabled[/green]\n"
        config_text += "  💻 Technology Analysis: [green]✅ Enabled[/green]\n"
        config_text += f"  📈 Sentiment Analysis: [{'green' if SERPAPI_API_KEY or SERPER_API_KEY else 'yellow'}]{'✅ Enabled' if SERPAPI_API_KEY or SERPER_API_KEY else '⚠️  Limited (missing search API)'}[/]\n"
        config_text += "  💡 Investment Recommendations: [green]✅ Enabled[/green]\n"
        
        console.print(Panel(
            config_text,
            title="⚙️ Configuration Status",
            border_style="blue"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Configuration check failed: {str(e)}[/red]")


if __name__ == "__main__":
    app()