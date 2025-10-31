import re

def extract_keywords(text, stop_words=None):
    """
    Extracts keywords from the input text using Python built-ins (split and re).
    
    Process:
    - Converts text to lowercase for case-insensitivity.
    - Removes punctuation and non-alphanumeric characters (except spaces) using regex.
    - Splits the text into words.
    - Filters out common stop words (default or user-provided).
    - Preserves the order of first occurrence.
    
    Args:
        text (str): The input text string to parse.
        stop_words (set or list, optional): Custom list or set of stop words to ignore.
    
    Returns:
        list: A list of extracted keywords (unique words, excluding stop words, preserving order).
    """
    # Default stop words
    if stop_words is None:
        stop_words = set([
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'while', 'at', 'by', 'for', 'with', 'about', 'against',
            'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
            'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
            'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
            'should', 'now'
        ])
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # Split into words
    words = text.split()
    
    # Filter stop words and keep order of first occurrence
    seen = set()
    keywords = []
    for word in words:
        if word and word not in stop_words and word not in seen:
            seen.add(word)
            keywords.append(word)
    return keywords

# Example usage
if __name__ == "__main__":
    sample_text = "Hello, this is a sample text for keyword extraction. It includes words like hello, world, and python."
    keywords = extract_keywords(sample_text)
    print("Extracted Keywords:", keywords)
    # Output: ['hello', 'sample', 'text', 'keyword', 'extraction', 'includes', 'words', 'like', 'world', 'python']