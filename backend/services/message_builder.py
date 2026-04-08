import re

def beautify_niche(niche_str):
    """
    Converts raw niche strings from the sheet into a clean, readable form.
    e.g. "fitness/LIFESTYLE" -> "Fitness / Lifestyle"
         "fitness fashion "  -> "Fitness Fashion"
         "Beauty,makeup"     -> "Beauty / Makeup"
    """
    if not niche_str:
        return ""
    # Normalise separators: / , & -> " / "
    niche_str = re.sub(r'\s*[/,&]\s*', ' / ', niche_str.strip())
    # Title case each word
    return " ".join(word.capitalize() for word in niche_str.split())


def build_message(template, final_price, brand_type, deliverables,
                  product_value=0, product_retainable="Yes",
                  creator_name="", creator_niche=""):
    """
    Prepares the outreach message by replacing placeholders.

    Supported variables:
        {{name}}              – Creator name from sheet
        {{niche}}             – Creator niche (beautified)
        {{rate}}              – Calculated final rate
        {{deliverables}}      – Number of videos from input
        {{product_value}}     – Product value from input
        {{retainable_line}}   – Conditional retainable / non-retainable sentence
        {{product_retainable}}– Raw "Yes" or "No"
        {{company_name}}      – Always INFLUENZE
        {{brand_type}}        – Brand type from input

    Rules:
        - Variables not present in template are ignored (left as-is)
        - Numbers are NOT auto-formatted (no currency symbols added)
    """
    if not template:
        return ""

    # --- Format numbers ---
    def fmt_num(v):
        try:
            v = float(v)
            return str(int(v)) if v == int(v) else str(v)
        except Exception:
            return str(v)

    formatted_price = fmt_num(final_price)
    formatted_product_value = fmt_num(product_value)
    beautified_niche = beautify_niche(str(creator_niche))

    # --- Build conditional retainable line ---
    status = str(product_retainable).strip().lower()
    if status == "yes":
        retainable_line = f"Product worth {formatted_product_value} will be retainable (no need to return)"
    elif status == "no":
        retainable_line = "You will receive the products but they are not retainable, brand will arrange the shipping"
    else:
        # "none", "not included", etc.
        retainable_line = ""

    # --- Replace variables ---
    message = template
    
    # Special handling for {{retainable_line}}:
    # If it's empty, we want to remove the entire line it's on (including common bullet points like • or *)
    if not retainable_line:
        # Regex explanation: 
        # ^[ \t]*[•*+\-\s]*      Matches start of line, any whitespace, then common bullet chars (+-\s escaped)
        # \{\{retainable_line\}\} Matches the exact placeholder
        # [ \t]*\n?            Matches any trailing whitespace and the newline
        import re
        message = re.sub(r'^[ \t]*[•*+\-\s]*\{\{retainable_line\}\}[ \t]*\n?', '', message, flags=re.MULTILINE)
    else:
        message = message.replace("{{retainable_line}}", retainable_line)

    # Standard replacements
    message = message.replace("{{name}}", str(creator_name))
    message = message.replace("{{niche}}", beautified_niche)
    message = message.replace("{{rate}}", formatted_price)
    message = message.replace("{{company_name}}", "INFLUENZE")
    message = message.replace("{{deliverables}}", str(deliverables))
    message = message.replace("{{product_value}}", formatted_product_value)
    message = message.replace("{{product_retainable}}", str(product_retainable))
    message = message.replace("{{brand_type}}", str(brand_type))

    return message
