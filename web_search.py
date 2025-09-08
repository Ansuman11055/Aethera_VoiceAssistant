import requests
from bs4 import BeautifulSoup
import wikipedia
import json
from typing import List, Dict
from config import MAX_SEARCH_RESULTS, SEARCH_SUMMARY_LENGTH

class WebSearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def search_web(self, query: str) -> Dict:
        """Primary web search function with multiple fallbacks"""
        try:
            # Method 1: Try Bing Search API (more reliable)
            result = self._bing_search(query)
            if result['success'] and result.get('summary'):
                return result
                
            # Method 2: Try DuckDuckGo Instant Answer
            result = self._duckduckgo_search(query)
            if result['success'] and result.get('summary'):
                return result
                
            # Method 3: Try Google search scraping as fallback
            result = self._google_search_fallback(query)
            if result['success']:
                return result
                
            # Method 4: Try Wikipedia as last resort
            return self._wikipedia_fallback(query)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'summary': f"I couldn't search for '{query}' right now. Please check your internet connection."
            }
    
    def _bing_search(self, query: str) -> Dict:
        """Try Bing search using their web interface"""
        try:
            url = "https://www.bing.com/search"
            params = {
                'q': query,
                'count': MAX_SEARCH_RESULTS,
                'setlang': 'en'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # Look for search results
            for result in soup.find_all('li', class_='b_algo')[:MAX_SEARCH_RESULTS]:
                try:
                    title_elem = result.find('h2')
                    snippet_elem = result.find('p')
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text().strip()
                        snippet = snippet_elem.get_text().strip()
                        
                        results.append({
                            'title': title,
                            'snippet': self._truncate_text(snippet, 100)
                        })
                except:
                    continue
            
            # Look for answer box or featured snippet
            answer_box = soup.find('div', class_='b_rs')
            if answer_box:
                answer_text = answer_box.get_text().strip()
                if answer_text:
                    return {
                        'success': True,
                        'query': query,
                        'abstract': answer_text,
                        'sources': results,
                        'summary': self._truncate_text(answer_text, SEARCH_SUMMARY_LENGTH)
                    }
            
            if results:
                summary_text = '. '.join([r['snippet'] for r in results[:2]])
                return {
                    'success': True,
                    'query': query,
                    'abstract': summary_text,
                    'sources': results,
                    'summary': self._truncate_text(summary_text, SEARCH_SUMMARY_LENGTH)
                }
                
            return {'success': False, 'error': 'No results found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _duckduckgo_search(self, query: str) -> Dict:
        """Try DuckDuckGo instant answer API"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            result = {
                'success': True,
                'query': query,
                'abstract': '',
                'sources': [],
                'summary': ''
            }
            
            # Check for instant answers
            if data.get('AbstractText'):
                result['abstract'] = data['AbstractText']
                result['summary'] = self._truncate_text(data['AbstractText'], SEARCH_SUMMARY_LENGTH)
            elif data.get('Definition'):
                result['abstract'] = data['Definition']
                result['summary'] = self._truncate_text(data['Definition'], SEARCH_SUMMARY_LENGTH)
            elif data.get('Answer'):
                result['abstract'] = data['Answer']
                result['summary'] = self._truncate_text(data['Answer'], SEARCH_SUMMARY_LENGTH)
            
            # Get related topics
            if data.get('RelatedTopics'):
                for topic in data['RelatedTopics'][:MAX_SEARCH_RESULTS]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        result['sources'].append({
                            'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                            'snippet': self._truncate_text(topic['Text'], 100),
                            'url': topic.get('FirstURL', '')
                        })
            
            if result['abstract']:
                return result
            else:
                return {'success': False, 'error': 'No instant answer available'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _google_search_fallback(self, query: str) -> Dict:
        """Google search scraping as fallback"""
        try:
            url = f"https://www.google.com/search"
            params = {'q': query, 'num': MAX_SEARCH_RESULTS}
            response = self.session.get(url, params=params, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            
            # Look for featured snippet first
            featured_snippet = soup.find('div', {'data-attrid': 'wa:/description'})
            if not featured_snippet:
                featured_snippet = soup.find('span', {'data-tts': 'answers'})
            
            if featured_snippet:
                snippet_text = featured_snippet.get_text().strip()
                if snippet_text:
                    return {
                        'success': True,
                        'query': query,
                        'abstract': snippet_text,
                        'sources': [{'title': 'Featured Result', 'snippet': snippet_text}],
                        'summary': self._truncate_text(snippet_text, SEARCH_SUMMARY_LENGTH)
                    }
            
            # Look for regular search results
            search_results = soup.find_all(['div', 'span'], class_=['BNeawe', 'VwiC3b'])
            
            current_title = None
            for elem in search_results:
                text = elem.get_text().strip()
                if not text:
                    continue
                    
                # Check if this looks like a title (shorter, no periods at the end usually)
                if len(text) < 100 and not text.endswith('.'):
                    current_title = text
                elif current_title and len(text) > 20:  # This looks like a snippet
                    results.append({
                        'title': current_title,
                        'snippet': self._truncate_text(text, 100)
                    })
                    current_title = None
                    
                    if len(results) >= MAX_SEARCH_RESULTS:
                        break
            
            if results:
                summary_text = '. '.join([r['snippet'] for r in results[:2]])
                return {
                    'success': True,
                    'query': query,
                    'abstract': summary_text,
                    'sources': results,
                    'summary': self._truncate_text(summary_text, SEARCH_SUMMARY_LENGTH)
                }
            
            return {'success': False, 'error': 'No search results found'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _wikipedia_fallback(self, query: str) -> Dict:
        """Use Wikipedia as final fallback"""
        try:
            wikipedia.set_lang("en")
            summary = wikipedia.summary(query, sentences=2)
            
            return {
                'success': True,
                'query': query,
                'abstract': summary,
                'sources': [{'title': 'Wikipedia', 'snippet': summary}],
                'summary': self._truncate_text(summary, SEARCH_SUMMARY_LENGTH)
            }
            
        except wikipedia.exceptions.DisambiguationError as e:
            try:
                summary = wikipedia.summary(e.options[0], sentences=2)
                return {
                    'success': True,
                    'query': query,
                    'abstract': summary,
                    'sources': [{'title': f'Wikipedia - {e.options[0]}', 'snippet': summary}],
                    'summary': self._truncate_text(summary, SEARCH_SUMMARY_LENGTH)
                }
            except:
                pass
        except:
            pass
            
        return {
            'success': False,
            'error': 'No information found',
            'summary': f"I couldn't find reliable information about '{query}'. Please try rephrasing your search."
        }
    
    def search_wikipedia(self, query: str) -> Dict:
        """Dedicated Wikipedia search"""
        try:
            wikipedia.set_lang("en")
            
            summary = wikipedia.summary(query, sentences=3)
            
            page = wikipedia.page(query)
            url = page.url
            
            return {
                'success': True,
                'query': query,
                'summary': summary,
                'url': url,
                'source': 'Wikipedia'
            }
            
        except wikipedia.exceptions.DisambiguationError as e:
            try:
                summary = wikipedia.summary(e.options[0], sentences=2)
                page = wikipedia.page(e.options[0])
                return {
                    'success': True,
                    'query': query,
                    'summary': f"Found information about {e.options[0]}: {summary}",
                    'url': page.url,
                    'source': 'Wikipedia'
                }
            except:
                return {
                    'success': False,
                    'error': 'Multiple topics found',
                    'summary': f"I found multiple topics for '{query}'. Could you be more specific?"
                }
                
        except wikipedia.exceptions.PageError:
            return {
                'success': False,
                'error': 'Page not found',
                'summary': f"I couldn't find a Wikipedia page for '{query}'."
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': f"Error searching Wikipedia for '{query}'."
            }
    
    def get_news_headlines(self, topic: str = "technology") -> Dict:
        """Get news headlines from RSS feeds"""
        try:
            rss_feeds = {
                'technology': 'https://feeds.bbci.co.uk/news/technology/rss.xml',
                'science': 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
                'business': 'https://feeds.bbci.co.uk/news/business/rss.xml',
                'world': 'https://feeds.bbci.co.uk/news/world/rss.xml'
            }
            
            feed_url = rss_feeds.get(topic.lower(), rss_feeds['technology'])
            
            response = self.session.get(feed_url, timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            
            headlines = []
            for item in soup.find_all('item')[:5]:
                title = item.title.text if item.title else "No title"
                description = item.description.text if item.description else ""
                
                headlines.append({
                    'title': title,
                    'description': self._truncate_text(description, 100)
                })
            
            if headlines:
                summary = f"Here are the latest {topic} headlines: " + \
                         ". ".join([h['title'] for h in headlines[:3]])
                
                return {
                    'success': True,
                    'headlines': headlines,
                    'summary': summary,
                    'topic': topic
                }
            else:
                return {
                    'success': False,
                    'summary': f"I couldn't fetch {topic} news right now."
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'summary': f"I couldn't fetch {topic} news right now."
            }
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length]
        last_sentence_end = max(
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )
        
        if last_sentence_end > max_length * 0.7:
            return truncated[:last_sentence_end + 1]
        else:
            return truncated.rsplit(' ', 1)[0] + "..."