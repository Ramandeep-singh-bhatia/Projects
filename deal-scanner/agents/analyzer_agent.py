"""
Deal Quality Analyzer Agent.
Uses OpenAI to analyze deal quality and calculate deal scores.
"""
import json
from typing import Dict, Any, Optional
from loguru import logger

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not installed. Deal analysis disabled.")

from config.settings import OPENAI_API_KEY, OPENAI_CONFIG, DEAL_ANALYSIS_CONFIG
from utils.database import db


class DealAnalyzerAgent:
    """Analyze deal quality using AI."""

    def __init__(self, api_key: str = None):
        """
        Initialize deal analyzer agent.

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.config = OPENAI_CONFIG
        self.enabled = OPENAI_AVAILABLE and self.api_key

        if self.enabled:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("Deal Analyzer Agent initialized")
        else:
            self.client = None
            logger.warning("Deal Analyzer Agent disabled - will use fallback scoring")

    def analyze_deal(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a deal and calculate quality score.

        Args:
            product: Product data dictionary

        Returns:
            Analysis results with score and recommendation
        """
        # Use AI analysis if available
        if self.enabled:
            try:
                return self._analyze_with_ai(product)
            except Exception as e:
                logger.error(f"Error in AI analysis: {e}")
                logger.info("Falling back to rule-based analysis")

        # Fallback to rule-based analysis
        return self._analyze_with_rules(product)

    def _analyze_with_ai(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze deal using OpenAI.

        Args:
            product: Product data dictionary

        Returns:
            Analysis results
        """
        prompt = self._create_analysis_prompt(product)

        response = self.client.chat.completions.create(
            model=self.config['model'],
            messages=[
                {"role": "system", "content": "You are a deal analysis expert. Analyze product deals and provide scores and recommendations in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config['temperature'],
            max_tokens=self.config['max_tokens'],
        )

        # Parse AI response
        content = response.choices[0].message.content

        try:
            # Try to extract JSON from response
            json_match = content
            if '```json' in content:
                json_match = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                json_match = content.split('```')[1].split('```')[0]

            result = json.loads(json_match.strip())

            logger.info(f"AI analysis complete: score={result.get('score')}, recommendation={result.get('recommendation')}")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response: {e}")
            logger.debug(f"Response content: {content}")
            # Fallback to rule-based
            return self._analyze_with_rules(product)

    def _analyze_with_rules(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze deal using rule-based logic.

        Args:
            product: Product data dictionary

        Returns:
            Analysis results
        """
        score = 0
        reasons = []

        current_price = product.get('current_price', 0)
        avg_price = product.get('average_price')
        lowest_price = product.get('lowest_price')
        previous_price = product.get('previous_price')
        rating = product.get('rating')
        review_count = product.get('review_count', 0)

        # 1. Price vs historical data (40% weight)
        price_score = 0
        if lowest_price and current_price:
            if current_price <= lowest_price:
                price_score = 40
                reasons.append("At historical low price")
            elif current_price <= lowest_price * 1.05:
                price_score = 35
                reasons.append("Within 5% of historical low")
            elif current_price <= lowest_price * 1.10:
                price_score = 30
                reasons.append("Within 10% of historical low")

        elif avg_price and current_price:
            discount = (avg_price - current_price) / avg_price
            if discount >= 0.30:
                price_score = 38
                reasons.append(f"30%+ below average price")
            elif discount >= 0.20:
                price_score = 32
                reasons.append(f"20%+ below average price")
            elif discount >= 0.15:
                price_score = 25
                reasons.append(f"15%+ below average price")

        elif previous_price and current_price:
            discount = (previous_price - current_price) / previous_price
            if discount >= 0.30:
                price_score = 35
                reasons.append(f"{discount*100:.0f}% off previous price")
            elif discount >= 0.20:
                price_score = 28
                reasons.append(f"{discount*100:.0f}% off previous price")
            elif discount >= 0.15:
                price_score = 20
                reasons.append(f"{discount*100:.0f}% off")

        score += price_score

        # 2. Product quality/reviews (30% weight)
        quality_score = 0
        if rating:
            if rating >= 4.5:
                quality_score = 30
                reasons.append(f"Excellent rating ({rating}/5)")
            elif rating >= 4.0:
                quality_score = 25
                reasons.append(f"Good rating ({rating}/5)")
            elif rating >= 3.5:
                quality_score = 18
                reasons.append(f"Average rating ({rating}/5)")
            elif rating >= 3.0:
                quality_score = 10
            else:
                quality_score = 0
                reasons.append(f"Low rating ({rating}/5)")

        # Adjust based on review count
        if review_count >= 1000:
            quality_score = min(30, quality_score + 5)
            reasons.append(f"Many reviews ({review_count})")
        elif review_count >= 100:
            quality_score = min(30, quality_score + 2)
        elif review_count < 10:
            quality_score = max(0, quality_score - 5)
            reasons.append("Few reviews")

        score += quality_score

        # 3. Timing/seasonality (15% weight)
        # Basic scoring - could be enhanced with seasonal logic
        timing_score = 10  # Base score
        score += timing_score

        # 4. Retailer reputation (15% weight)
        retailer_score = 15  # Base score for known retailers
        retailer = product.get('retailer', '').lower()
        if retailer in ['amazon', 'bestbuy', 'walmart']:
            retailer_score = 15
        score += retailer_score

        # Determine recommendation
        if score >= 80:
            recommendation = "BUY_NOW"
        elif score >= 70:
            recommendation = "GOOD_DEAL"
        elif score >= 50:
            recommendation = "CONSIDER"
        else:
            recommendation = "WAIT"

        return {
            'score': int(score),
            'reasoning': ' | '.join(reasons) if reasons else 'Standard pricing',
            'recommendation': recommendation,
            'price_score': price_score,
            'quality_score': quality_score,
        }

    def _create_analysis_prompt(self, product: Dict[str, Any]) -> str:
        """Create analysis prompt for OpenAI."""
        title = product.get('title', 'Unknown Product')
        category = product.get('category', 'Unknown')
        current_price = product.get('current_price', 0)
        avg_price = product.get('average_price', 'N/A')
        lowest_price = product.get('lowest_price', 'N/A')
        previous_price = product.get('previous_price', 'N/A')
        rating = product.get('rating', 'N/A')
        review_count = product.get('review_count', 0)

        prompt = f"""
Analyze this product deal and provide a score 0-100:

Product: {title}
Category: {category}
Current Price: ${current_price}
Historical Average: ${avg_price}
Historical Low: ${lowest_price}
Previous Price: ${previous_price}
Rating: {rating}/5 stars
Review Count: {review_count}

Consider:
1. Price vs historical data (40% weight)
2. Product quality/reviews (30% weight)
3. Timing/seasonality (15% weight)
4. Retailer reputation (15% weight)

Respond ONLY with valid JSON in this exact format:
{{
  "score": <number 0-100>,
  "reasoning": "<brief explanation>",
  "recommendation": "<BUY_NOW|GOOD_DEAL|CONSIDER|WAIT>"
}}
"""
        return prompt

    def should_notify(self, analysis: Dict[str, Any]) -> bool:
        """
        Determine if a deal should trigger a notification.

        Args:
            analysis: Analysis results

        Returns:
            True if should notify, False otherwise
        """
        score = analysis.get('score', 0)
        min_score = DEAL_ANALYSIS_CONFIG['min_deal_score']

        return score >= min_score

    def enrich_product_data(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich product data with deal analysis.

        Args:
            product: Product data dictionary

        Returns:
            Enriched product data
        """
        # Get historical data from database if available
        product_id = product.get('product_id')
        if product_id:
            db_product = db.get_product_by_id(product_id)
            if db_product:
                product['average_price'] = db_product.get('average_price')
                product['lowest_price'] = db_product.get('lowest_price')
                product['highest_price'] = db_product.get('highest_price')

        # Analyze deal
        analysis = self.analyze_deal(product)

        # Add analysis to product data
        product['deal_score'] = analysis['score']
        product['deal_reasoning'] = analysis['reasoning']
        product['deal_recommendation'] = analysis['recommendation']

        return product


# Singleton instance
analyzer = DealAnalyzerAgent()
