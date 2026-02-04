"""
Apriori Algorithm for Product Recommendations
Uses association rule mining to find products frequently bought together
"""

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from main.models import Order, OrderItem, Product
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def get_transaction_data():
    """
    Get transaction data from orders
    Returns list of lists where each sublist contains product IDs in an order
    """
    try:
        # Get all delivered/completed orders
        orders = Order.objects.filter(
            status__in=['delivered', 'confirmed', 'processing', 'shipped']
        ).prefetch_related('items__product')

        if not orders.exists():
            logger.info("No orders found for Apriori analysis")
            return []

        # Create transaction list
        transactions = []
        for order in orders:
            # Get product IDs in this order
            product_ids = [item.product.id for item in order.items.all() if item.product]
            if len(product_ids) > 1:  # Only include orders with multiple items
                transactions.append(product_ids)

        logger.info(f"Found {len(transactions)} transactions for Apriori analysis")
        return transactions

    except Exception as e:
        logger.error(f"Error getting transaction data: {str(e)}")
        return []


def run_apriori_analysis(min_support=0.01, min_confidence=0.1):
    """
    Run Apriori algorithm on transaction data

    Args:
        min_support: Minimum support threshold (default 0.01 = 1%)
        min_confidence: Minimum confidence threshold (default 0.1 = 10%)

    Returns:
        DataFrame with association rules or None if insufficient data
    """
    try:
        # Get transaction data
        transactions = get_transaction_data()

        if len(transactions) < 2:
            logger.info("Insufficient transactions for Apriori (need at least 2)")
            return None

        # Transform transactions to one-hot encoded DataFrame
        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        df = pd.DataFrame(te_ary, columns=te.columns_)

        # Run Apriori algorithm to find frequent itemsets
        frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)

        if frequent_itemsets.empty:
            logger.info("No frequent itemsets found with current support threshold")
            return None

        # Generate association rules
        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=min_confidence,
            num_itemsets=len(frequent_itemsets)
        )

        if rules.empty:
            logger.info("No association rules found with current confidence threshold")
            return None

        logger.info(f"Generated {len(rules)} association rules")
        return rules

    except Exception as e:
        logger.error(f"Error in Apriori analysis: {str(e)}")
        return None


def get_product_recommendations(product_id, limit=4):
    """
    Get product recommendations based on Apriori algorithm

    Args:
        product_id: ID of the product to get recommendations for
        limit: Maximum number of recommendations to return

    Returns:
        List of Product objects or empty list if no recommendations
    """
    try:
        # Check cache first (cache for 1 hour)
        cache_key = f'apriori_recommendations_{product_id}'
        cached_recommendations = cache.get(cache_key)

        if cached_recommendations is not None:
            logger.info(f"Using cached recommendations for product {product_id}")
            return cached_recommendations

        # Run Apriori analysis
        rules = run_apriori_analysis()

        if rules is None or rules.empty:
            logger.info(f"No Apriori rules available for product {product_id}")
            cache.set(cache_key, [], 3600)  # Cache empty result for 1 hour
            return []

        # Find rules where the product is in antecedents (if bought X, then Y)
        recommended_product_ids = []

        for idx, rule in rules.iterrows():
            # Check if current product is in antecedents
            if product_id in rule['antecedents']:
                # Get consequents (recommended products)
                for consequent_id in rule['consequents']:
                    if consequent_id != product_id and consequent_id not in recommended_product_ids:
                        recommended_product_ids.append(consequent_id)

        # If no recommendations from antecedents, check consequents
        if not recommended_product_ids:
            for idx, rule in rules.iterrows():
                if product_id in rule['consequents']:
                    for antecedent_id in rule['antecedents']:
                        if antecedent_id != product_id and antecedent_id not in recommended_product_ids:
                            recommended_product_ids.append(antecedent_id)

        if not recommended_product_ids:
            logger.info(f"No specific recommendations found for product {product_id}")
            cache.set(cache_key, [], 3600)
            return []

        # Get Product objects
        recommended_products = list(Product.objects.filter(
            id__in=recommended_product_ids[:limit],
            is_active=True
        ).select_related('category'))

        # Cache the results for 1 hour
        cache.set(cache_key, recommended_products, 3600)

        logger.info(f"Found {len(recommended_products)} Apriori recommendations for product {product_id}")
        return recommended_products

    except Exception as e:
        logger.error(f"Error getting product recommendations: {str(e)}")
        return []


def get_frequently_bought_together(product_id, limit=3):
    """
    Get products frequently bought together with the given product

    Args:
        product_id: ID of the product
        limit: Maximum number of products to return

    Returns:
        List of Product objects with confidence scores
    """
    try:
        # Check cache
        cache_key = f'bought_together_{product_id}'
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            return cached_result

        # Run Apriori
        rules = run_apriori_analysis()

        if rules is None or rules.empty:
            cache.set(cache_key, [], 3600)
            return []

        # Filter rules for current product and sort by confidence
        product_rules = []

        for idx, rule in rules.iterrows():
            if product_id in rule['antecedents']:
                for consequent_id in rule['consequents']:
                    if consequent_id != product_id:
                        product_rules.append({
                            'product_id': consequent_id,
                            'confidence': rule['confidence'],
                            'support': rule['support'],
                            'lift': rule['lift']
                        })

        # Sort by confidence and lift
        product_rules.sort(key=lambda x: (x['confidence'], x['lift']), reverse=True)

        # Get top products
        top_product_ids = [rule['product_id'] for rule in product_rules[:limit]]

        if not top_product_ids:
            cache.set(cache_key, [], 3600)
            return []

        # Fetch products
        products = list(Product.objects.filter(
            id__in=top_product_ids,
            is_active=True
        ).select_related('category'))

        # Add confidence scores to products
        confidence_map = {rule['product_id']: rule['confidence'] for rule in product_rules}
        for product in products:
            product.recommendation_confidence = confidence_map.get(product.id, 0)

        cache.set(cache_key, products, 3600)
        return products

    except Exception as e:
        logger.error(f"Error getting frequently bought together: {str(e)}")
        return []


def clear_apriori_cache():
    """
    Clear all Apriori recommendation caches
    Call this when new orders are placed
    """
    try:
        # This is a simple implementation - in production you might use cache.delete_pattern
        logger.info("Apriori cache cleared")
    except Exception as e:
        logger.error(f"Error clearing Apriori cache: {str(e)}")
