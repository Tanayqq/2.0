import re

def clean_chunk_content(text: str) -> str:
    if not text:
        return ""

    # 1. Remove label cross-references like [see Warnings and Precautions (5.1)], [see Dosage and Administration (2.1)]
    text = re.sub(r'\[see\s+[^\]]+\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(see\s+[^)]+\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[see\s*[^\]]*\]', '', text, flags=re.IGNORECASE) # safety catch

    # 2. Remove Section/Table/Figure references (e.g., Section 5.2, Table 1, Figure 2)
    text = re.sub(r'\bSection\s+\d+(\.\d+)?\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bTable\s+\d+\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bFigure\s+\d+\b', '', text, flags=re.IGNORECASE)

    # 3. Remove FDA decimal numbering (e.g. 5.1, 5.2, 6.1, 12.1)
    text = re.sub(r'\b\d+\.\d+\b', '', text)

    # Split into lines to process lists and collapse internal whitespace
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # Collapse multiple horizontal whitespaces
        collapsed = re.sub(r'[ \t]+', ' ', stripped)
        
        # 4. Convert lists into plain bullets (e.g. 1. Hypersensitivity -> • Hypersensitivity)
        # Handle lines starting with -, *, •, or numbered lists
        match_bullet = re.match(r'^[-*•]\s*(.*)', collapsed)
        match_num = re.match(r'^\d+\.?\s*(.*)', collapsed)
        
        if match_bullet:
            content = match_bullet.group(1).strip()
            if content:
                cleaned_lines.append(f"• {content}")
        elif match_num:
            content = match_num.group(1).strip()
            if content:
                cleaned_lines.append(f"• {content}")
        else:
            cleaned_lines.append(collapsed)

    # 5. Remove duplicated lines/paragraphs
    seen = set()
    final_lines = []
    for cl in cleaned_lines:
        # Strip trailing/leading punctuation for deduplication check to catch minor variations
        norm = re.sub(r'[^\w\s]', '', cl).strip().lower()
        if norm not in seen:
            seen.add(norm)
            final_lines.append(cl)

    return "\n".join(final_lines)
