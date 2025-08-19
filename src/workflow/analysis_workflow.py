"""
LangGraph workflow for multi-agent ticker analysis with RAG integration
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("[WARN] LangGraph not available. Install with: pip install langgraph")

from ..config.display_config import safe_format
from ..tool.RAG.vector_store import knowledge_store
from ..agent.ticker_analyzer import MultiAgentTickerAnalyzer


class AnalysisState(dict):
    """State class for the analysis workflow"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Required fields
        self.setdefault('ticker', '')
        self.setdefault('company_name', '')
        self.setdefault('current_step', 'validation')
        self.setdefault('results', {})
        self.setdefault('context', {})
        self.setdefault('errors', [])
        self.setdefault('completed_analyses', [])


class TickerAnalysisWorkflow:
    """LangGraph-based workflow for ticker analysis"""
    
    def __init__(self, analyzer: MultiAgentTickerAnalyzer = None):
        self.analyzer = analyzer or MultiAgentTickerAnalyzer()
        self.workflow = None
        self.app = None
        
        # Analysis steps mapping
        self.analysis_steps = {
            'cash_flow': 'cash_flow_analyzer',
            'profit': 'profit_analyzer', 
            'ceo': 'ceo_analyzer',
            'technology': 'technology_analyzer',
            'sentiment': 'sentiment_analyzer'
        }
        
        if LANGGRAPH_AVAILABLE:
            self._build_workflow()
    
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(AnalysisState)
        
        # Add nodes
        workflow.add_node("validate_ticker", self.validate_ticker)
        workflow.add_node("prepare_analysis", self.prepare_analysis)
        workflow.add_node("cash_flow_analysis", self.cash_flow_analysis)
        workflow.add_node("profit_analysis", self.profit_analysis)
        workflow.add_node("ceo_analysis", self.ceo_analysis)
        workflow.add_node("technology_analysis", self.technology_analysis)
        workflow.add_node("sentiment_analysis", self.sentiment_analysis)
        workflow.add_node("compile_results", self.compile_results)
        workflow.add_node("handle_error", self.handle_error)
        
        # Set entry point
        workflow.set_entry_point("validate_ticker")
        
        # Add edges
        workflow.add_conditional_edges(
            "validate_ticker",
            self._validation_router,
            {
                "valid": "prepare_analysis",
                "invalid": "handle_error"
            }
        )
        
        workflow.add_edge("prepare_analysis", "cash_flow_analysis")
        workflow.add_edge("cash_flow_analysis", "profit_analysis")
        workflow.add_edge("profit_analysis", "ceo_analysis")
        workflow.add_edge("ceo_analysis", "technology_analysis")
        workflow.add_edge("technology_analysis", "sentiment_analysis")
        workflow.add_edge("sentiment_analysis", "compile_results")
        workflow.add_edge("compile_results", END)
        workflow.add_edge("handle_error", END)
        
        # Compile workflow
        memory = MemorySaver()
        self.app = workflow.compile(checkpointer=memory)
        
        print(safe_format("[OK] LangGraph workflow compiled successfully"))
    
    def _validation_router(self, state: AnalysisState) -> str:
        """Route based on validation result"""
        return "valid" if not state.get('errors') else "invalid"
    
    async def validate_ticker(self, state: AnalysisState) -> AnalysisState:
        """Validate ticker and basic data"""
        ticker = state['ticker']
        
        print(safe_format(f"[VALIDATE] Checking ticker: {ticker}"))
        
        # Get RAG context for validation
        validation_context = knowledge_store.get_context_for_analysis(
            "investment", 
            {"ticker": ticker}
        )
        
        # Use analyzer's validation
        test_data = self.analyzer.cash_flow_analyzer.get_financial_data(ticker)
        
        if 'error' in test_data:
            state['errors'].append(test_data['error'])
            state['current_step'] = 'error'
        else:
            state['current_step'] = 'validation_passed'
            state['context']['company_data'] = test_data
            state['company_name'] = test_data.get('longName', ticker)
            
            if validation_context:
                state['context']['validation_knowledge'] = validation_context
        
        return state
    
    async def prepare_analysis(self, state: AnalysisState) -> AnalysisState:
        """Prepare for analysis with RAG context"""
        print(safe_format("[PREPARE] Setting up analysis context"))
        
        # Get comprehensive RAG context for all analysis types
        for analysis_type in self.analysis_steps.keys():
            context = knowledge_store.get_context_for_analysis(
                analysis_type,
                state['context'].get('company_data', {})
            )
            if context:
                state['context'][f'{analysis_type}_knowledge'] = context
        
        state['current_step'] = 'analysis_prepared'
        return state
    
    async def cash_flow_analysis(self, state: AnalysisState) -> AnalysisState:
        """Perform cash flow analysis with RAG enhancement"""
        return await self._perform_analysis(state, 'cash_flow', 'Cash Flow Analysis')
    
    async def profit_analysis(self, state: AnalysisState) -> AnalysisState:
        """Perform profit analysis with RAG enhancement"""
        return await self._perform_analysis(state, 'profit', 'Profit Analysis')
    
    async def ceo_analysis(self, state: AnalysisState) -> AnalysisState:
        """Perform CEO analysis with RAG enhancement"""
        return await self._perform_analysis(state, 'ceo', 'CEO Analysis')
    
    async def technology_analysis(self, state: AnalysisState) -> AnalysisState:
        """Perform technology analysis with RAG enhancement"""
        return await self._perform_analysis(state, 'technology', 'Technology Analysis')
    
    async def sentiment_analysis(self, state: AnalysisState) -> AnalysisState:
        """Perform sentiment analysis with RAG enhancement"""
        return await self._perform_analysis(state, 'sentiment', 'Sentiment Analysis')
    
    async def _perform_analysis(self, state: AnalysisState, analysis_type: str, display_name: str) -> AnalysisState:
        """Generic analysis performer with RAG integration"""
        ticker = state['ticker']
        company_name = state.get('company_name', '')
        
        print(safe_format(f"[ANALYZE] {display_name} for {ticker}"))
        
        try:
            # Get the analyzer
            analyzer_name = self.analysis_steps[analysis_type]
            analyzer = getattr(self.analyzer, analyzer_name)
            
            # Get RAG context
            rag_context = state['context'].get(f'{analysis_type}_knowledge', '')
            
            # Perform analysis with enhanced context
            if hasattr(analyzer, 'analyze_with_context'):
                # If analyzer supports RAG context
                result = analyzer.analyze_with_context(
                    ticker, 
                    company_name,
                    context=rag_context
                )
            else:
                # Fallback to normal analysis
                if analysis_type == 'cash_flow':
                    result = analyzer.analyze_cash_flow_and_revenue(ticker, company_name)
                elif analysis_type == 'profit':
                    result = analyzer.analyze_profit_margins(ticker, company_name)
                elif analysis_type == 'ceo':
                    result = analyzer.analyze_ceo_performance(ticker, company_name)
                elif analysis_type == 'technology':
                    result = analyzer.analyze_technology_competitive_advantage(ticker, company_name)
                elif analysis_type == 'sentiment':
                    result = analyzer.analyze_market_sentiment(ticker, company_name)
            
            # Store result with RAG context if available
            enriched_result = result.copy() if isinstance(result, dict) else {'analysis': result}
            if rag_context:
                enriched_result['rag_context'] = rag_context
                enriched_result['enhanced'] = True
            
            state['results'][analysis_type] = enriched_result
            state['completed_analyses'].append(analysis_type)
            state['current_step'] = f'{analysis_type}_completed'
            
        except Exception as e:
            error_msg = f"Error in {display_name}: {str(e)}"
            print(safe_format(f"[FAIL] {error_msg}"))
            state['errors'].append(error_msg)
            state['results'][analysis_type] = {'error': error_msg}
        
        return state
    
    async def compile_results(self, state: AnalysisState) -> AnalysisState:
        """Compile all analysis results"""
        print(safe_format("[COMPILE] Generating final report"))
        
        # Get investment context from RAG
        investment_context = knowledge_store.get_context_for_analysis(
            "investment",
            state['context'].get('company_data', {})
        )
        
        # Use analyzer's compilation method
        final_result = {
            'ticker': state['ticker'],
            'company_name': state.get('company_name', ''),
            'analysis_timestamp': datetime.now().isoformat(),
            'workflow_version': '1.0',
            'rag_enhanced': True,
            'completed_analyses': state['completed_analyses'],
            'individual_results': state['results'],
            'investment_framework': investment_context if investment_context else '',
            'errors': state['errors']
        }
        
        # Add comprehensive summary
        if len(state['completed_analyses']) >= 3:
            summary_parts = []
            for analysis in state['completed_analyses']:
                result = state['results'].get(analysis, {})
                if isinstance(result, dict) and 'analysis' in result:
                    summary_parts.append(f"{analysis.title()}: {result['analysis'][:200]}...")
            
            final_result['executive_summary'] = ' | '.join(summary_parts)
        
        state['final_result'] = final_result
        state['current_step'] = 'completed'
        
        return state
    
    async def handle_error(self, state: AnalysisState) -> AnalysisState:
        """Handle errors in the workflow"""
        print(safe_format(f"[ERROR] Analysis failed: {state['errors']}"))
        
        state['final_result'] = {
            'ticker': state['ticker'],
            'analysis_status': 'failed',
            'errors': state['errors'],
            'timestamp': datetime.now().isoformat()
        }
        state['current_step'] = 'error_handled'
        
        return state
    
    def get_workflow_visualization(self) -> Dict[str, Any]:
        """Get workflow structure for visualization"""
        if not LANGGRAPH_AVAILABLE:
            return {
                "error": "LangGraph not available",
                "steps": list(self.analysis_steps.keys())
            }
        
        return {
            "workflow_type": "ticker_analysis",
            "nodes": [
                {"id": "validate_ticker", "type": "validation", "description": "Validate ticker and fetch basic data"},
                {"id": "prepare_analysis", "type": "preparation", "description": "Prepare RAG context for all analyses"},
                {"id": "cash_flow_analysis", "type": "analysis", "description": "Analyze cash flow and R&D spending"},
                {"id": "profit_analysis", "type": "analysis", "description": "Analyze profit margins and profitability"},
                {"id": "ceo_analysis", "type": "analysis", "description": "Analyze CEO and leadership performance"},
                {"id": "technology_analysis", "type": "analysis", "description": "Analyze technology competitive advantage"},
                {"id": "sentiment_analysis", "type": "analysis", "description": "Analyze market sentiment and perception"},
                {"id": "compile_results", "type": "compilation", "description": "Compile final investment analysis"},
                {"id": "handle_error", "type": "error", "description": "Handle analysis errors"}
            ],
            "edges": [
                {"from": "validate_ticker", "to": "prepare_analysis", "condition": "valid"},
                {"from": "validate_ticker", "to": "handle_error", "condition": "invalid"},
                {"from": "prepare_analysis", "to": "cash_flow_analysis"},
                {"from": "cash_flow_analysis", "to": "profit_analysis"},
                {"from": "profit_analysis", "to": "ceo_analysis"},
                {"from": "ceo_analysis", "to": "technology_analysis"},
                {"from": "technology_analysis", "to": "sentiment_analysis"},
                {"from": "sentiment_analysis", "to": "compile_results"},
                {"from": "compile_results", "to": "END"},
                {"from": "handle_error", "to": "END"}
            ],
            "rag_integration": True,
            "analysis_types": list(self.analysis_steps.keys())
        }
    
    async def analyze_ticker_with_workflow(
        self, 
        ticker: str, 
        company_name: Optional[str] = None,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Run complete ticker analysis through workflow"""
        
        if not LANGGRAPH_AVAILABLE:
            print(safe_format("[WARN] LangGraph not available, falling back to sequential analysis"))
            return await self._fallback_analysis(ticker, company_name)
        
        # Prepare initial state
        initial_state = AnalysisState(
            ticker=ticker.upper(),
            company_name=company_name or '',
            config=config or {}
        )
        
        try:
            # Run workflow
            config = {"configurable": {"thread_id": f"analysis_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}}
            
            final_state = None
            async for state in self.app.astream(initial_state, config):
                final_state = state
                # Print progress
                current_step = list(state.keys())[0] if state else "unknown"
                if current_step != "END":
                    print(safe_format(f"[WORKFLOW] Completed step: {current_step}"))
            
            return final_state.get('final_result', {
                'error': 'Workflow completed but no final result',
                'ticker': ticker
            })
            
        except Exception as e:
            print(safe_format(f"[ERROR] Workflow execution failed: {e}"))
            return {
                'ticker': ticker,
                'analysis_status': 'workflow_failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _fallback_analysis(self, ticker: str, company_name: Optional[str] = None) -> Dict[str, Any]:
        """Fallback to sequential analysis without LangGraph"""
        print(safe_format("[FALLBACK] Running sequential analysis"))
        
        # Use the original analyzer
        return self.analyzer.analyze_ticker_comprehensive(
            ticker, 
            company_name, 
            force_new=False
        )


# Global workflow instance
analysis_workflow = TickerAnalysisWorkflow()