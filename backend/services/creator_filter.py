import re

def clean_phone_number(phone_str):
    """
    Cleans a phone number by removing country codes (+91), leading zeros, 
    and all non-digit characters. Returns exactly 10 digits if valid, else None.
    """
    if not phone_str:
        return None
    
    # Remove all non-digits, handling potential .0 from float conversion
    s = str(phone_str).strip()
    if s.endswith('.0'):
        s = s[:-2]
    digits = re.sub(r'\D', '', s)
    
    # Case 1: 12 digits starting with 91 (International format like +91...)
    if len(digits) == 12 and digits.startswith('91'):
        digits = digits[2:]
    
    # Case 2: 11 digits starting with 0 (Standard leading zero format)
    elif len(digits) == 11 and digits.startswith('0'):
        digits = digits[1:]
        
    # Final check: Must be exactly 10 digits now
    if len(digits) == 10:
        return digits
    
    return None

def filter_creators(creators, brand_requirements, contacted_creators):
    """
    Filters and sorts creators based on brand requirements and rules.
    Empty inputs = ignore filter.
    
    Args:
        creators (list[dict]): List of creator dicts from Google Sheets.
        brand_requirements (dict): {
            "niches": [str],
            "budget": float,
            "deliverables": int,
            "allowed_category": [str],
            "brand_type": str
        }
        contacted_creators (list[dict]): List of logs to check for prior contact.
        
    Returns:
        list[dict]: List of suitable creators, sorted by priority.
    """
    suitable_creators = []
    
    brand_name = brand_requirements.get("brand_type", "").lower()
    target_niches = [n.lower() for n in brand_requirements.get("target_niches", brand_requirements.get("niches", [])) if n.strip()]
    allowed_categories = [c.lower() for c in brand_requirements.get("creator_categories", brand_requirements.get("allowed_category", [])) if c.strip()]
    
    # 1. Calculate per-video budget
    max_budget = float(brand_requirements.get("max_budget", brand_requirements.get("budget", 0)))
    deliverables = int(brand_requirements.get("deliverables", 1))
    if deliverables < 1: deliverables = 1
    per_video_budget = max_budget / deliverables if max_budget > 0 else 0
    
    # helper to check if already contacted
    contacted_map = set() # (creator_name/phone, brand_name)
    for log in contacted_creators:
        c_name = str(log.get("Name", "")).lower()
        b_name = str(log.get("Brand", "")).lower()
        contacted_map.add((c_name, b_name))


    for creator in creators:
        # Data Extraction & Normalization
        # --- Robust Column Name Detection ---
        raw_phone = ""
        phone_keys = ["number", "whatsapp", "contact", "mobile", "phone", "wa"]
        # Also grab Name/Rate/IG robustly
        creator_name = ""
        creator_rate_str = "0"
        creator_ig = ""
        
        for key, val in creator.items():
            k_low = key.strip().lower()
            if any(pk == k_low for pk in phone_keys) or any(pk in k_low for pk in phone_keys):
                if not raw_phone: raw_phone = val
            if "name" in k_low:
                creator_name = str(val).strip()
            if "rate" in k_low or "price" in k_low:
                creator_rate_str = str(val).strip()
            if "ig" in k_low or "insta" in k_low or "link" in k_low:
                # If multiple link columns, favor those with "ig" or "insta"
                if "ig" in k_low or "insta" in k_low or not creator_ig:
                    creator_ig = str(val).strip()
        
        if not creator_name:
            creator_name = str(creator.get("Name", "")).strip()

        if not creator_name: continue
        
        cleaned_phone = clean_phone_number(raw_phone)
        if not cleaned_phone:
            continue
        
        c_niche = str(creator.get("Niche", "")).lower().strip()
        category = str(creator.get("Category", "")).strip()
        
        # Use the robustly extracted rate string
        raw_rate_str = creator_rate_str.lower()
        
        matches = re.findall(r'(\d+(?:\.\d+)?)\s*(k?)', raw_rate_str)
        prices = []
        
        # If price column accidentally contains an Instagram link / URL, avoid parsing its digits
        if "http" not in raw_rate_str and "www." not in raw_rate_str:
            for num_str, k_suffix in matches:
                val = float(num_str)
                if k_suffix == 'k':
                    val *= 1000
                prices.append(val)
            
        if prices:
            rate = sum(prices) / len(prices)
        else:
            rate = 99999999.0
            
        # --- Strict Filtering Rules ---
        # Rule 0: Skip filter if input is empty
        
        # 1. Niche matches required niche (if provided)
        if target_niches:
            if not any(t in c_niche for t in target_niches):
                continue

        # 2. Category matches (if provided and creator has a category)
        if allowed_categories and category:
            if category.lower() not in allowed_categories:
                continue
            
        # 3. Rate logic (if budget > 0)
        # creator_rate ∈ (per_video_budget ± 2000)
        if per_video_budget > 0:
            if not ((per_video_budget - 2000) <= rate <= (per_video_budget + 2000)):
                continue

        # 4. Not already contacted for SAME brand type (always run)
        if (creator_name.lower(), brand_name) in contacted_map:
            continue
            
        # If passed all, calculate final message rate and add
        offer_per_video = min(per_video_budget, rate) if per_video_budget > 0 else rate
        final_message_rate = offer_per_video * deliverables
        
        creator['Name'] = creator_name # Sync back for preview
        creator['IG Link'] = creator_ig # Sync back for preview
        creator['parsed_rate'] = rate
        creator['parsed_category'] = category
        creator['final_message_rate'] = final_message_rate
        creator['cleaned_phone'] = cleaned_phone
        suitable_creators.append(creator)
        
    # --- Sorting / Priority ---
    # Priority order:
    # 1. Good category
    # 2. Average category
    # 3. Rate closest to brand budget
    
    def sort_key(c):
        cat = c['parsed_category'].lower()
        # Lower score is better
        if cat == 'category a' or cat == 'good':
            cat_score = 1
        elif cat == 'category b' or cat == 'average':
            cat_score = 2
        elif cat == 'category c':
            cat_score = 3
        elif cat == 'category d':
            cat_score = 4
        else:
            cat_score = 5
        
        rate_diff = abs(c['parsed_rate'] - per_video_budget)
        
        return (cat_score, rate_diff)
        
    suitable_creators.sort(key=sort_key)
    
    return suitable_creators
