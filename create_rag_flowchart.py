#!/usr/bin/env python3
"""
Create RAG Flow Chart for AI Ticker Analyzer
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def create_rag_flowchart():
    """Create a comprehensive RAG flow chart"""
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Define colors
    colors = {
        'input': '#E3F2FD',      # Light blue
        'rag': '#FFF3E0',        # Light orange  
        'analysis': '#E8F5E8',   # Light green
        'output': '#F3E5F5',     # Light purple
        'arrow': '#424242',      # Dark gray
        'border': '#2E2E2E'      # Almost black
    }
    
    # Helper function to create rounded rectangle
    def create_box(x, y, width, height, text, color, text_size=10):
        box = FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.1",
            facecolor=color,
            edgecolor=colors['border'],
            linewidth=1.5
        )
        ax.add_patch(box)
        
        # Add text
        ax.text(x + width/2, y + height/2, text,
               ha='center', va='center',
               fontsize=text_size, weight='bold',
               wrap=True)
    
    # Helper function to create arrow
    def create_arrow(start_x, start_y, end_x, end_y, text=''):
        ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                   arrowprops=dict(arrowstyle='->', lw=2, color=colors['arrow']))
        if text:
            mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
            ax.text(mid_x, mid_y, text, ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                   fontsize=8)
    
    # Title
    ax.text(8, 11, 'AI Ticker Analyzer - RAG Enhanced Architecture', 
           ha='center', va='center', fontsize=18, weight='bold')
    
    # 1. Input Layer
    create_box(1, 9.5, 2.5, 1, 'User Input\n(Ticker: NVDA)', colors['input'], 11)
    create_box(4.5, 9.5, 2.5, 1, 'Validation\n& Data Fetch', colors['input'], 11)
    
    # 2. RAG Knowledge Store Layer
    create_box(0.5, 7.5, 3, 1.5, 'RAG Knowledge Store\n\n• Financial Ratios\n• R&D Analysis\n• Leadership\n• Technology\n• Sentiment\n• Investment', colors['rag'], 9)
    
    create_box(4, 7.5, 2.5, 1.5, 'Vector Search\n(FAISS)\n\nSentence\nTransformers', colors['rag'], 9)
    
    create_box(7, 7.5, 2.5, 1.5, 'Context\nRetrieval\n\nSimilarity\nMatching', colors['rag'], 9)
    
    # 3. Analysis Modules with RAG Enhancement
    analysis_modules = [
        ('Cash Flow\nAnalysis', 1, 5.5),
        ('Profit\nAnalysis', 3, 5.5),
        ('CEO\nAnalysis', 5, 5.5), 
        ('Technology\nAnalysis', 7, 5.5),
        ('Sentiment\nAnalysis', 9, 5.5)
    ]
    
    for name, x, y in analysis_modules:
        create_box(x, y, 1.5, 1, name, colors['analysis'], 9)
        create_box(x, y-1.5, 1.5, 1, f'RAG\nContext', colors['rag'], 8)
    
    # 4. LLM Processing Layer
    create_box(2, 2.5, 6, 1, 'LLM Analysis (Gemini/OpenAI)\nEnhanced with RAG Context', colors['analysis'], 11)
    
    # 5. Output Layer
    create_box(1, 0.5, 2, 1, 'Analysis\nResults', colors['output'], 10)
    create_box(3.5, 0.5, 2, 1, 'Workflow\nVisualization', colors['output'], 10)
    create_box(6, 0.5, 2, 1, 'Investment\nRecommendation', colors['output'], 10)
    create_box(8.5, 0.5, 2, 1, 'Reports &\nCharts', colors['output'], 10)
    
    # Arrows - Input Flow
    create_arrow(2.25, 9.5, 2.25, 9, '')
    create_arrow(3.5, 10, 4.5, 10, '')
    create_arrow(5.75, 9.5, 5.75, 9, '')
    
    # Arrows - RAG Flow
    create_arrow(2, 7.5, 2, 7, 'Knowledge\nQuery')
    create_arrow(3.5, 8.25, 4, 8.25, '')
    create_arrow(6.5, 8.25, 7, 8.25, '')
    
    # Arrows - Context to Analysis
    for _, x, y in analysis_modules:
        create_arrow(x + 0.75, 7.5, x + 0.75, 6.5, '')
        create_arrow(x + 0.75, 4.5, x + 0.75, 4, '')
    
    # Arrows - Analysis to LLM
    create_arrow(2.25, 4, 3, 3.5, '')
    create_arrow(3.75, 4, 4, 3.5, '')
    create_arrow(5.75, 4, 6, 3.5, '')
    create_arrow(7.75, 4, 7, 3.5, '')
    create_arrow(9.75, 4, 8, 3.5, '')
    
    # Arrows - LLM to Output
    create_arrow(3, 2.5, 2, 1.5, '')
    create_arrow(4.5, 2.5, 4.5, 1.5, '')
    create_arrow(6, 2.5, 7, 1.5, '')
    create_arrow(7, 2.5, 9.5, 1.5, '')
    
    # Add side panel with RAG benefits
    create_box(11, 8, 3.5, 3, 'RAG Benefits:\n\n• Context-Aware Analysis\n• Industry Best Practices\n• Consistent Frameworks\n• Enhanced Accuracy\n• Knowledge Integration\n• Scalable Intelligence', '#FFE0B2', 9)
    
    # Add workflow panel
    create_box(11, 4, 3.5, 3, 'Workflow Features:\n\n• State Management\n• Error Recovery\n• Visual Pipeline\n• Async Processing\n• Graph Visualization\n• Interactive Charts', '#E1F5FE', 9)
    
    # Set axis properties
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Add footer
    ax.text(7.5, 0.1, '[ROCKET] AI-Powered Financial Analysis with RAG Enhancement & LangGraph Orchestration', 
           ha='center', va='center', fontsize=12, style='italic')
    
    plt.tight_layout()
    plt.savefig('RAG_Flow_Chart.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("[OK] RAG Flow Chart created: RAG_Flow_Chart.png")

if __name__ == "__main__":
    create_rag_flowchart()