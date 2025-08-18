import tweepy
import requests
from newsapi import NewsApiClient
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
from typing import Dict, Any, List
import time
from datetime import datetime, timedelta
import os
from src.config import SERPAPI_API_KEY, SERPER_API_KEY


class SentimentAnalyzer:
    """Analyzes market sentiment using news sources and Twitter/X"""
    
    def __init__(self):
        self.serp_api_key = SERPAPI_API_KEY
        self.serper_api_key = SERPER_API_KEY
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Twitter API credentials (user needs to add these to .env)
        self.twitter_bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')
        self.twitter_client = None
        
        if self.twitter_bearer_token:
            try:
                self.twitter_client = tweepy.Client(bearer_token=self.twitter_bearer_token)
            except Exception as e:
                print(f"Twitter client initialization failed: {e}")
    
    def get_company_info(self, ticker: str) -> Dict[str, Any]:
        """Get basic company information for sentiment analysis"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'company_name': info.get('longName', ticker),
                'ticker': ticker,
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A')
            }
        except Exception as e:
            return {'error': f"Failed to get company info: {str(e)}"}
    
    def search_news_sentiment(self, company_name: str, ticker: str) -> Dict[str, Any]:
        """Search for recent news articles and analyze sentiment"""
        try:
            news_data = {
                'articles': [],
                'sentiment_scores': [],
                'overall_sentiment': 0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
            
            # Search queries for comprehensive coverage
            search_queries = [
                f"{company_name} {ticker} earnings financial results",
                f"{company_name} news today recent developments",
                f"{company_name} stock market analysis outlook",
                f"{company_name} CEO management leadership news"
            ]
            
            all_articles = []
            
            # Use SERP API if available
            if self.serper_api_key:
                for query in search_queries:
                    try:
                        articles = self.search_with_serper(query)
                        all_articles.extend(articles)
                        time.sleep(1)  # Rate limiting
                    except Exception as e:
                        print(f"SERP search failed for '{query}': {e}")
                        continue
            
            # Analyze sentiment for each article
            for article in all_articles[:20]:  # Limit to 20 articles
                try:
                    title = article.get('title', '')
                    snippet = article.get('snippet', '')
                    text = f"{title} {snippet}"
                    
                    if text.strip():
                        # TextBlob sentiment
                        blob = TextBlob(text)
                        polarity = blob.sentiment.polarity
                        
                        # VADER sentiment
                        vader_scores = self.vader_analyzer.polarity_scores(text)
                        compound = vader_scores['compound']
                        
                        # Combined sentiment score
                        combined_sentiment = (polarity + compound) / 2
                        
                        sentiment_category = 'neutral'
                        if combined_sentiment > 0.1:
                            sentiment_category = 'positive'
                        elif combined_sentiment < -0.1:
                            sentiment_category = 'negative'
                        
                        article_data = {
                            'title': title,
                            'snippet': snippet,
                            'url': article.get('link', ''),
                            'sentiment_score': combined_sentiment,
                            'sentiment_category': sentiment_category,
                            'source': article.get('source', 'N/A')
                        }
                        
                        news_data['articles'].append(article_data)
                        news_data['sentiment_scores'].append(combined_sentiment)
                        news_data['sentiment_distribution'][sentiment_category] += 1
                        
                except Exception as e:
                    print(f"Error analyzing article sentiment: {e}")
                    continue
            
            # Calculate overall sentiment
            if news_data['sentiment_scores']:
                news_data['overall_sentiment'] = sum(news_data['sentiment_scores']) / len(news_data['sentiment_scores'])
            
            return news_data
            
        except Exception as e:
            return {'error': f"Failed to analyze news sentiment: {str(e)}"}
    
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
            
            articles = []
            for result in data.get('organic', []):
                articles.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'link': result.get('link', ''),
                    'source': result.get('source', '')
                })
            
            return articles
            
        except Exception as e:
            print(f"Serper search error: {e}")
            return []
    
    def search_twitter_sentiment(self, company_name: str, ticker: str) -> Dict[str, Any]:
        """Search Twitter/X for sentiment analysis"""
        try:
            twitter_data = {
                'tweets': [],
                'sentiment_scores': [],
                'overall_sentiment': 0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'tweet_count': 0
            }
            
            if not self.twitter_client:
                return {'error': 'Twitter API not configured. Please add TWITTER_BEARER_TOKEN to .env file'}
            
            # Search queries for Twitter
            search_queries = [
                f"${ticker}",
                f"{company_name}",
                f"${ticker} stock",
                f"{company_name} earnings"
            ]
            
            all_tweets = []
            
            for query in search_queries:
                try:
                    tweets = tweepy.Paginator(
                        self.twitter_client.search_recent_tweets,
                        query=query,
                        max_results=50,
                        tweet_fields=['created_at', 'public_metrics']
                    ).flatten(limit=100)
                    
                    all_tweets.extend(tweets)
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"Twitter search failed for '{query}': {e}")
                    continue
            
            # Remove duplicates
            unique_tweets = {tweet.id: tweet for tweet in all_tweets}
            
            # Analyze sentiment for each tweet
            for tweet in list(unique_tweets.values())[:100]:  # Limit to 100 tweets
                try:
                    text = tweet.text
                    
                    # Clean tweet text
                    text = ' '.join(word for word in text.split() if not word.startswith(('@', '#', 'http')))
                    
                    if len(text.strip()) > 10:  # Skip very short texts
                        # TextBlob sentiment
                        blob = TextBlob(text)
                        polarity = blob.sentiment.polarity
                        
                        # VADER sentiment
                        vader_scores = self.vader_analyzer.polarity_scores(text)
                        compound = vader_scores['compound']
                        
                        # Combined sentiment score
                        combined_sentiment = (polarity + compound) / 2
                        
                        sentiment_category = 'neutral'
                        if combined_sentiment > 0.1:
                            sentiment_category = 'positive'
                        elif combined_sentiment < -0.1:
                            sentiment_category = 'negative'
                        
                        tweet_data = {
                            'text': text[:200],  # Truncate for storage
                            'created_at': str(tweet.created_at),
                            'sentiment_score': combined_sentiment,
                            'sentiment_category': sentiment_category,
                            'retweet_count': tweet.public_metrics['retweet_count'] if hasattr(tweet, 'public_metrics') else 0
                        }
                        
                        twitter_data['tweets'].append(tweet_data)
                        twitter_data['sentiment_scores'].append(combined_sentiment)
                        twitter_data['sentiment_distribution'][sentiment_category] += 1
                        
                except Exception as e:
                    print(f"Error analyzing tweet sentiment: {e}")
                    continue
            
            twitter_data['tweet_count'] = len(twitter_data['tweets'])
            
            # Calculate overall sentiment
            if twitter_data['sentiment_scores']:
                twitter_data['overall_sentiment'] = sum(twitter_data['sentiment_scores']) / len(twitter_data['sentiment_scores'])
            
            return twitter_data
            
        except Exception as e:
            return {'error': f"Failed to analyze Twitter sentiment: {str(e)}"}
    
    def combine_sentiment_analysis(self, news_data: Dict[str, Any], twitter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine news and Twitter sentiment for overall analysis"""
        try:
            combined_analysis = {
                'news_sentiment': news_data.get('overall_sentiment', 0),
                'twitter_sentiment': twitter_data.get('overall_sentiment', 0),
                'combined_sentiment': 0,
                'sentiment_confidence': 0,
                'sentiment_category': 'neutral',
                'data_sources': {
                    'news_articles': len(news_data.get('articles', [])),
                    'tweets_analyzed': twitter_data.get('tweet_count', 0)
                },
                'sentiment_breakdown': {
                    'news_distribution': news_data.get('sentiment_distribution', {}),
                    'twitter_distribution': twitter_data.get('sentiment_distribution', {})
                }
            }
            
            # Calculate weighted combined sentiment
            news_weight = 0.6  # Give more weight to news
            twitter_weight = 0.4
            
            if news_data.get('overall_sentiment') is not None and twitter_data.get('overall_sentiment') is not None:
                combined_analysis['combined_sentiment'] = (
                    news_data['overall_sentiment'] * news_weight +
                    twitter_data['overall_sentiment'] * twitter_weight
                )
                combined_analysis['sentiment_confidence'] = 0.9
            elif news_data.get('overall_sentiment') is not None:
                combined_analysis['combined_sentiment'] = news_data['overall_sentiment']
                combined_analysis['sentiment_confidence'] = 0.7
            elif twitter_data.get('overall_sentiment') is not None:
                combined_analysis['combined_sentiment'] = twitter_data['overall_sentiment']
                combined_analysis['sentiment_confidence'] = 0.6
            else:
                combined_analysis['sentiment_confidence'] = 0.1
            
            # Determine overall sentiment category
            sentiment_score = combined_analysis['combined_sentiment']
            if sentiment_score > 0.15:
                combined_analysis['sentiment_category'] = 'positive'
            elif sentiment_score < -0.15:
                combined_analysis['sentiment_category'] = 'negative'
            else:
                combined_analysis['sentiment_category'] = 'neutral'
            
            return combined_analysis
            
        except Exception as e:
            return {'error': f"Failed to combine sentiment analysis: {str(e)}"}
    
    def analyze_sentiment_complete(self, ticker: str) -> Dict[str, Any]:
        """Complete sentiment analysis combining news and Twitter data"""
        try:
            # Get company info
            company_info = self.get_company_info(ticker)
            
            if 'error' in company_info:
                return company_info
            
            company_name = company_info['company_name']
            
            # Analyze news sentiment
            news_data = self.search_news_sentiment(company_name, ticker)
            
            # Analyze Twitter sentiment
            twitter_data = self.search_twitter_sentiment(company_name, ticker)
            
            # Combine analyses
            combined_analysis = self.combine_sentiment_analysis(news_data, twitter_data)
            
            return {
                'ticker': ticker,
                'company_info': company_info,
                'news_analysis': news_data,
                'twitter_analysis': twitter_data,
                'combined_sentiment': combined_analysis,
                'analysis_summary': {
                    'overall_sentiment_score': combined_analysis.get('combined_sentiment', 0),
                    'sentiment_category': combined_analysis.get('sentiment_category', 'neutral'),
                    'confidence_level': combined_analysis.get('sentiment_confidence', 0),
                    'data_quality': {
                        'news_articles_analyzed': len(news_data.get('articles', [])),
                        'tweets_analyzed': twitter_data.get('tweet_count', 0)
                    },
                    'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
        except Exception as e:
            return {'error': f"Failed to complete sentiment analysis: {str(e)}"}