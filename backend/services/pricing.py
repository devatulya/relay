def calculate_final_price(brand_budget, creator_rate):
    """
    Calculates the final offer price for a creator.
    Formula: min(brand_budget, creator_rate)
    
    Args:
        brand_budget (float): The maximum budget the brand is willing to pay.
        creator_rate (float): The creator's asking rate.
        
    Returns:
        float: The final price to offer.
    """
    try:
        budget = float(brand_budget)
        rate = float(creator_rate)
        return min(budget, rate)
    except (ValueError, TypeError):
        # Fallback or error handling if inputs are invalid
        # For safety/logic, if we can't parse, return 0 or raise
        # But per requirements "price closest to brand budget", we assume valid inputs pre-validated
        return 0.0
