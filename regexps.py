import re
from string import punctuation

# Pattern for time recognition during search query
time_pattern = re.compile(r'([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])*')
# Pattern for date recognition during search query
date_pattern = re.compile(r'(3[01]|[12]\d|0?[1-9])[./-](1[012]|0?[1-9])([./-]((?:19|20)\d{2}|\d\d))*')
# Endings for the text recognition pattern
wrapper = '[\W\s]*'
# Pattern to insert between words for the text recognition pattern
midst = '[\W\s]+'


def create_text_regex(text):
    # Purges the text from punctuation and creates a regex for text recognition
    text_pattern = re.compile('[%s]' % re.escape(punctuation))
    text = text_pattern.sub('', text)

    # Text pattern looks like r'[\W\s]*sample[\W\s]+text[\W\s]*', ignoring all the non-word and whitespace characters
    text = text.lower().split()
    text_pattern = wrapper + midst.join(text) + wrapper
    text_pattern = re.compile(text_pattern, flags=re.I)

    return text_pattern
