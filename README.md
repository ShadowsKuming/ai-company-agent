# 🚀 AI Ticker Analyzer & Investment Recommender

A comprehensive AI-powered system for analyzing company stocks and generating investment recommendations based on 5 key dimensions:

1. **Cash Flow Analysis** - Revenue streams and R&D investment ratio
2. **Profit Mechanism Analysis** - How the company generates and maintains profits
3. **CEO & Leadership Analysis** - Leadership effectiveness and future impact potential
4. **Technology & IP Analysis** - Innovation capacity and competitive tech position  
5. **Market Sentiment Analysis** - News and social media sentiment

## 🎯 Features

- **Multi-LLM Support**: Uses Gemini Pro (default) or ChatGPT-4o
- **Comprehensive Analysis**: 5-dimensional company evaluation
- **Investment Recommendations**: AI-powered buy/hold/sell recommendations with detailed reasoning
- **Rich Reports**: Generates markdown reports, interactive charts, and structured data
- **Future-Focused**: Emphasizes R&D investment and innovation potential
- **Real-time Data**: Integrates multiple data sources (financial, news, social media)

## 🔧 Setup

### 1. Environment Setup

```bash
# Create conda environment
conda env create -f environment.yml
conda activate ai-company-agent
```

### 2. API Keys Configuration

Add the following to your `.env` file:

```env
# Required LLM APIs (at least one)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Required for comprehensive analysis
SERPER_API_KEY=your_serper_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here

# Optional for Twitter sentiment analysis
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
```

### 3. Install Additional Dependencies

Some packages might need to be installed separately:

```bash
pip install google-search-results
pip install googlesearch-python
```

## 🚀 Usage

### Command Line Interface

```bash
# Run comprehensive analysis for a ticker
python src/app.py analyze AAPL

# Use OpenAI instead of Gemini
python src/app.py analyze AAPL --llm openai

# Analysis without investment recommendation
python src/app.py analyze AAPL --no-recommend

# Generate recommendation for previously analyzed ticker
python src/app.py recommend AAPL

# Check analysis status
python src/app.py status AAPL

# View configuration
python src/app.py config
```

### Python API Usage

```python
# Quick analysis
from src.agent.ticker_analyzer import analyze_ticker
from src.agent.investment_recommender import get_investment_recommendation

# Analyze a company
result = analyze_ticker('AAPL', use_llm='gemini')

# Get investment recommendation
recommendation = get_investment_recommendation('AAPL', use_llm='gemini')
```

### Advanced Usage

```python
# Use individual agents
from src.agent.ticker_analyzer import TickerAnalyzerAgent
from src.agent.investment_recommender import InvestmentRecommenderAgent

# Initialize agents
analyzer = TickerAnalyzerAgent(use_llm='gemini')
recommender = InvestmentRecommenderAgent(use_llm='openai')

# Run comprehensive analysis
analysis = analyzer.analyze_ticker_comprehensive('AAPL')

# Generate recommendation
recommendation = recommender.recommend_investment('AAPL')
```

## 📊 Analysis Output

### Report Structure

```
reports/
├── AAPL/
│   ├── AAPL_comprehensive_report_20241201_143022.md
│   ├── investment_recommendation_20241201_143525.md
│   ├── analysis/
│   ├── charts/
│   │   ├── AAPL_rd_ratio.html
│   │   ├── AAPL_revenue_trend.html
│   │   ├── AAPL_profit_margins.html
│   │   ├── AAPL_sentiment_analysis.html
│   │   └── AAPL_technology_radar.html
│   └── raw_data/
│       ├── cash_flow_analysis_20241201_143022.json
│       ├── ceo_analysis_20241201_143045.json
│       ├── technology_analysis_20241201_143134.json
│       ├── sentiment_analysis_20241201_143201.json
│       └── profit_analysis_20241201_143089.json
```

### Key Metrics

The system generates scores (0-10) for:
- **Future Focus Score**: Based on R&D investment ratio
- **Leadership Impact Score**: CEO effectiveness and vision
- **Technology Score**: Innovation capacity and IP strength
- **Financial Health Score**: Profitability and stability
- **Market Sentiment Score**: News and social media sentiment
- **Overall Investment Score**: Weighted combination of all factors

### Investment Recommendations

- **STRONG BUY** (8.0-10.0): High confidence positive recommendation
- **BUY** (6.5-7.9): Positive recommendation with medium-high confidence
- **HOLD** (5.0-6.4): Neutral position recommendation
- **WEAK HOLD** (3.5-4.9): Cautious hold with medium-low confidence
- **SELL** (0-3.4): Negative recommendation

## 🔍 Analysis Components

### 1. Cash Flow Analysis
- Revenue stream identification and analysis
- R&D investment ratio calculation and trends
- Future-focused scoring based on innovation investment

### 2. Profit Analysis
- Profit margin analysis (gross, operating, net)
- Return on equity and assets
- Profitability trend analysis

### 3. CEO & Leadership Analysis
- CEO background research (education, experience)
- Leadership style and effectiveness assessment
- Technical competency evaluation
- Future impact potential scoring

### 4. Technology & IP Analysis
- Patent portfolio assessment
- Technology stack analysis
- Innovation capacity evaluation
- Competitive technology position

### 5. Sentiment Analysis
- News sentiment analysis from multiple sources
- Twitter/X social media sentiment
- Combined sentiment scoring with confidence levels

## ⚙️ Configuration

### LLM Selection
- **Gemini Pro**: Default, optimized for analysis tasks
- **ChatGPT-4o**: Alternative, good for detailed reasoning

### API Requirements
- **Essential**: At least one LLM API (Gemini or OpenAI)
- **Recommended**: SERPER API for comprehensive web search
- **Optional**: Twitter API for social sentiment, additional search APIs

### Data Sources
- **Financial Data**: Yahoo Finance
- **News**: Web scraping + SERP API
- **Social Media**: Twitter API v2
- **Company Info**: Web scraping + public databases
- **Patent Data**: Patent database searches

## 🚨 Important Notes

### Disclaimers
- This tool is for **informational purposes only**
- **Not personalized investment advice**
- Always consult qualified financial advisors
- Conduct your own research before making investment decisions

### Rate Limiting
- APIs have rate limits - analysis may take 2-5 minutes per ticker
- Twitter API has stricter limits
- Consider running analysis during off-peak hours

### Data Quality
- Results depend on data availability and API access
- Some companies may have limited public information
- Sentiment analysis reflects recent news/social media only

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Errors**: Check `.env` file and API key validity
2. **Import Errors**: Ensure all dependencies are installed
3. **Rate Limiting**: Wait between requests, check API quotas
4. **Missing Data**: Some analysis components may have limited data for certain companies

### Support
For issues and feature requests, check the codebase or create an issue.

## 📈 Example Analysis Flow

```bash
# 1. Check configuration
python src/app.py config

# 2. Run analysis
python src/app.py analyze AAPL --llm gemini

# 3. Check results
python src/app.py status AAPL

# 4. Generate additional recommendation
python src/app.py recommend AAPL --llm openai
```

---

**Built with**: Python, LangGraph, Gemini Pro, ChatGPT-4o, Yahoo Finance, Twitter API, SERP APIs