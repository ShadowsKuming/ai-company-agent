"""
Workflow visualization utilities for agent analysis graphs
"""

import json
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, Any, List, Optional
import matplotlib.patches as patches
from pathlib import Path
import datetime

try:
    import plotly.graph_objects as go
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("[WARN] Plotly not available. Install with: pip install plotly")

from ..config.display_config import safe_format


class WorkflowVisualizer:
    """Visualize agent analysis workflows"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_matplotlib_graph(
        self, 
        workflow_data: Dict[str, Any], 
        ticker: str = "",
        save_path: Optional[str] = None
    ) -> str:
        """Create workflow visualization using matplotlib"""
        
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        
        # Create networkx graph
        G = nx.DiGraph()
        
        # Color mapping for node types
        color_map = {
            'validation': '#FF6B6B',    # Red
            'preparation': '#4ECDC4',   # Teal  
            'analysis': '#45B7D1',      # Blue
            'compilation': '#96CEB4',   # Green
            'error': '#FFEAA7'          # Yellow
        }
        
        # Add nodes
        nodes = workflow_data.get('nodes', [])
        for node in nodes:
            G.add_node(node['id'], 
                      type=node.get('type', 'unknown'),
                      description=node.get('description', ''))
        
        # Add edges
        edges = workflow_data.get('edges', [])
        for edge in edges:
            if edge['to'] != 'END':
                label = edge.get('condition', '')
                G.add_edge(edge['from'], edge['to'], condition=label)
        
        # Position nodes using hierarchical layout
        pos = self._hierarchical_layout(G, nodes)
        
        # Draw nodes with colors based on type
        for node, (x, y) in pos.items():
            node_data = next((n for n in nodes if n['id'] == node), {})
            node_type = node_data.get('type', 'unknown')
            color = color_map.get(node_type, '#95A5A6')
            
            # Draw node
            circle = patches.Circle((x, y), 0.15, facecolor=color, 
                                  edgecolor='black', linewidth=2)
            ax.add_patch(circle)
            
            # Add node label
            ax.text(x, y-0.25, node.replace('_', '\n'), 
                   ha='center', va='top', fontsize=8, weight='bold')
            
            # Add description
            description = node_data.get('description', '')[:50] + '...' if len(node_data.get('description', '')) > 50 else node_data.get('description', '')
            ax.text(x, y-0.4, description, 
                   ha='center', va='top', fontsize=6, style='italic')
        
        # Draw edges
        for edge in G.edges(data=True):
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]
            
            # Draw arrow
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', lw=1.5, color='#2C3E50'))
            
            # Add condition label if exists
            condition = edge[2].get('condition', '')
            if condition:
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(mid_x, mid_y, condition, ha='center', va='center',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8),
                       fontsize=6)
        
        # Create legend
        legend_elements = [patches.Patch(color=color, label=type_name.title()) 
                          for type_name, color in color_map.items()]
        ax.legend(handles=legend_elements, loc='upper right')
        
        # Set title and clean up axes
        title = f"AI Agent Analysis Workflow"
        if ticker:
            title += f" - {ticker}"
        if workflow_data.get('rag_integration'):
            title += " (RAG Enhanced)"
        
        ax.set_title(title, fontsize=16, weight='bold', pad=20)
        ax.set_xlim(-1, 3)
        ax.set_ylim(-3, 1)
        ax.axis('off')
        
        # Add metadata
        metadata_text = f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        metadata_text += f"Analysis Types: {', '.join(workflow_data.get('analysis_types', []))}\n"
        metadata_text += f"RAG Integration: {'Yes' if workflow_data.get('rag_integration') else 'No'}"
        
        ax.text(0.02, 0.02, metadata_text, transform=ax.transAxes, fontsize=8,
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        
        # Save the plot
        if not save_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"workflow_graph_{ticker}_{timestamp}.png" if ticker else f"workflow_graph_{timestamp}.png"
            save_path = self.output_dir / filename
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(safe_format(f"[OK] Workflow graph saved: {save_path}"))
        return str(save_path)
    
    def create_plotly_graph(
        self,
        workflow_data: Dict[str, Any],
        ticker: str = "",
        save_path: Optional[str] = None
    ) -> str:
        """Create interactive workflow visualization using Plotly"""
        
        if not PLOTLY_AVAILABLE:
            print(safe_format("[WARN] Plotly not available, cannot create interactive graph"))
            return self.create_matplotlib_graph(workflow_data, ticker, save_path)
        
        # Create networkx graph for layout
        G = nx.DiGraph()
        nodes = workflow_data.get('nodes', [])
        edges = workflow_data.get('edges', [])
        
        for node in nodes:
            G.add_node(node['id'])
        
        for edge in edges:
            if edge['to'] != 'END':
                G.add_edge(edge['from'], edge['to'])
        
        # Get positions
        pos = self._hierarchical_layout(G, nodes)
        
        # Color mapping
        color_map = {
            'validation': '#FF6B6B',
            'preparation': '#4ECDC4', 
            'analysis': '#45B7D1',
            'compilation': '#96CEB4',
            'error': '#FFEAA7'
        }
        
        # Create traces for nodes
        node_trace = go.Scatter(
            x=[], y=[], text=[], textposition='middle center',
            mode='markers+text',
            hoverinfo='text',
            marker=dict(size=50, line=dict(width=2, color='black')),
            textfont=dict(size=12, color='white')
        )
        
        # Add nodes
        for node in nodes:
            if node['id'] in pos:
                x, y = pos[node['id']]
                node_trace['x'] += (x,)
                node_trace['y'] += (y,)
                
                node_type = node.get('type', 'unknown')
                color = color_map.get(node_type, '#95A5A6')
                
                node_trace['text'] += (node['id'].replace('_', '<br>'),)
                node_trace['marker']['color'] = node_trace['marker'].get('color', []) + [color]
                
                # Hover text
                hover_text = f"<b>{node['id']}</b><br>{node.get('description', '')}<br>Type: {node_type}"
                node_trace['hovertext'] = node_trace.get('hovertext', []) + [hover_text]
        
        # Create traces for edges
        edge_trace = go.Scatter(
            x=[], y=[], mode='lines',
            line=dict(width=2, color='#2C3E50'),
            hoverinfo='none'
        )
        
        # Add edges
        for edge in edges:
            if edge['to'] != 'END' and edge['from'] in pos and edge['to'] in pos:
                x0, y0 = pos[edge['from']]
                x1, y1 = pos[edge['to']]
                
                edge_trace['x'] += (x0, x1, None)
                edge_trace['y'] += (y0, y1, None)
        
        # Create the figure
        fig = go.Figure(data=[edge_trace, node_trace])
        
        # Update layout
        title = f"AI Agent Analysis Workflow"
        if ticker:
            title += f" - {ticker}"
        if workflow_data.get('rag_integration'):
            title += " (RAG Enhanced)"
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="Interactive Agent Workflow Graph<br>Hover over nodes for details",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='gray', size=10)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        # Save the plot
        if not save_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"workflow_interactive_{ticker}_{timestamp}.html" if ticker else f"workflow_interactive_{timestamp}.html"
            save_path = self.output_dir / filename
        
        pyo.plot(fig, filename=str(save_path), auto_open=False)
        
        print(safe_format(f"[OK] Interactive workflow graph saved: {save_path}"))
        return str(save_path)
    
    def _hierarchical_layout(self, G: nx.DiGraph, nodes: List[Dict]) -> Dict[str, tuple]:
        """Create hierarchical layout for workflow visualization"""
        # Define levels based on workflow structure
        levels = {
            'validate_ticker': 0,
            'prepare_analysis': 1,
            'cash_flow_analysis': 2,
            'profit_analysis': 2.5,
            'ceo_analysis': 2.5,
            'technology_analysis': 2.5,
            'sentiment_analysis': 2.5,
            'compile_results': 3,
            'handle_error': 1
        }
        
        # Position nodes
        pos = {}
        for node in nodes:
            node_id = node['id']
            level = levels.get(node_id, 2)
            
            # Horizontal positioning based on node type and level
            if node_id == 'validate_ticker':
                x_pos = 1
            elif node_id == 'prepare_analysis':
                x_pos = 1
            elif node_id == 'handle_error':
                x_pos = 2.5
            elif node_id == 'compile_results':
                x_pos = 1
            else:  # Analysis nodes
                analysis_nodes = ['cash_flow_analysis', 'profit_analysis', 'ceo_analysis', 'technology_analysis', 'sentiment_analysis']
                if node_id in analysis_nodes:
                    idx = analysis_nodes.index(node_id)
                    x_pos = 0.2 + (idx * 0.4)  # Spread across horizontally
            
            pos[node_id] = (x_pos, -level)
        
        return pos
    
    def create_analysis_summary_chart(
        self,
        analysis_results: Dict[str, Any],
        ticker: str = "",
        save_path: Optional[str] = None
    ) -> str:
        """Create summary chart of analysis results"""
        
        # Extract analysis scores/ratings
        analysis_data = []
        for analysis_type, result in analysis_results.get('individual_results', {}).items():
            if isinstance(result, dict) and not result.get('error'):
                # Extract some kind of score or rating
                score = self._extract_score_from_analysis(result)
                analysis_data.append({
                    'type': analysis_type.replace('_', ' ').title(),
                    'score': score,
                    'enhanced': result.get('enhanced', False)
                })
        
        if not analysis_data:
            return ""
        
        # Create bar chart
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        
        types = [item['type'] for item in analysis_data]
        scores = [item['score'] for item in analysis_data]
        enhanced = [item['enhanced'] for item in analysis_data]
        
        # Color bars based on RAG enhancement
        colors = ['#45B7D1' if enh else '#95A5A6' for enh in enhanced]
        
        bars = ax.bar(types, scores, color=colors, alpha=0.8)
        
        # Add value labels on bars
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{score:.1f}', ha='center', va='bottom')
        
        # Customize chart
        ax.set_ylabel('Analysis Score')
        ax.set_title(f'Analysis Results Summary - {ticker}' if ticker else 'Analysis Results Summary')
        ax.set_ylim(0, 5)
        
        # Add legend
        legend_elements = [
            patches.Patch(color='#45B7D1', label='RAG Enhanced'),
            patches.Patch(color='#95A5A6', label='Standard Analysis')
        ]
        ax.legend(handles=legend_elements)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save
        if not save_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_summary_{ticker}_{timestamp}.png" if ticker else f"analysis_summary_{timestamp}.png"
            save_path = self.output_dir / filename
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(safe_format(f"[OK] Analysis summary chart saved: {save_path}"))
        return str(save_path)
    
    def _extract_score_from_analysis(self, result: Dict[str, Any]) -> float:
        """Extract a numerical score from analysis result"""
        # Simple heuristic to extract score from text analysis
        analysis_text = str(result.get('analysis', ''))
        
        # Look for common rating patterns
        if 'excellent' in analysis_text.lower() or '5/5' in analysis_text:
            return 5.0
        elif 'good' in analysis_text.lower() or 'strong' in analysis_text.lower():
            return 4.0
        elif 'average' in analysis_text.lower() or 'moderate' in analysis_text.lower():
            return 3.0
        elif 'poor' in analysis_text.lower() or 'weak' in analysis_text.lower():
            return 2.0
        elif 'very poor' in analysis_text.lower() or 'terrible' in analysis_text.lower():
            return 1.0
        else:
            return 3.5  # Default neutral score
    
    def generate_workflow_report(
        self,
        workflow_data: Dict[str, Any],
        analysis_results: Dict[str, Any],
        ticker: str = ""
    ) -> Dict[str, str]:
        """Generate complete workflow visualization report"""
        
        report_paths = {}
        
        try:
            # Create matplotlib graph
            graph_path = self.create_matplotlib_graph(workflow_data, ticker)
            report_paths['workflow_graph'] = graph_path
            
            # Create interactive graph if possible
            interactive_path = self.create_plotly_graph(workflow_data, ticker)
            report_paths['interactive_graph'] = interactive_path
            
            # Create summary chart
            if analysis_results:
                summary_path = self.create_analysis_summary_chart(analysis_results, ticker)
                if summary_path:
                    report_paths['summary_chart'] = summary_path
            
            print(safe_format(f"[OK] Complete workflow visualization generated for {ticker}"))
            
        except Exception as e:
            print(safe_format(f"[ERROR] Failed to generate workflow visualization: {e}"))
        
        return report_paths


# Global visualizer instance
workflow_visualizer = WorkflowVisualizer()