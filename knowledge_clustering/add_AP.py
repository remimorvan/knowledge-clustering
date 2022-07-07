import knowledge_clustering.add_quotes as quotes
import re  # Regular expressions

INTRO_STRING = ["\intro", '""']
AP_STRING = ["\AP", "\itemAP"]


def missing_AP(text, space, size_tab=4):
    text_cleaned, pointer = quotes.ignore_spaces(text)
    at_what_line, at_what_col = quotes.compute_line_col(text, size_tab)
    for i_str in INTRO_STRING:
        for i_match in re.finditer(re.escape(i_str), text_cleaned):
            start = i_match.start()
            beg = max(0, start - space)
            if not True in [ap_str in text_cleaned[beg:start] for ap_str in AP_STRING]:
                message = (
                    f"Missing anchor point at line {at_what_line[pointer[start]]}."
                )
                print(message)
