"""
    Analyze the task narrative or the description of the gamelevel and
    compute a score that mesures how difficult the comprehension is.
"""
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import cmudict
from hyphenate import hyphenate_word


# dictionary that tracks the list of phonemes per word
phoneme_dict = dict(cmudict.entries())

# Track number of phonemes
num_phoneme = {k:len(phoneme_dict[k]) for k in phoneme_dict}


def get_description(gamelevel):
    """
    Query the database and return the task narrative.
    """
    narrative = ""

    return narrative


def reading_difficulty(text):
    """
    https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_reading_ease
    """
    words = [w for w in word_tokenize(text) if w.isalpha()]

    num_word = len(words)

    #for w in words:
    #    print(w, phoneme_dict[w], hyphenate_word(w))

    #num_syll = sum(num_phoneme[w] for w in words if w in num_phoneme)
    num_syll = sum(len(hyphenate_word(w)) for w in words)

    num_sent = len(sent_tokenize(text))
    #print(num_sent, num_word, num_syll)

    # Calculate Flesch-reading-ease
    flesch = 206.835 - 1.015 * (num_word / num_sent) - 84.6 * (num_syll / num_word)
    #print(flesch)

    diff_idx = 1 - flesch / 100

    if diff_idx < 0 or diff_idx > 1:
        if diff_idx < 0:
            diff_idx = 0
        else:
            diff_idx = 1

    return diff_idx


if __name__ == "__main__":
    txt = "This sentence, taken as a reading passage unto itself, is being used to prove a point."
    txt = "The Australian platypus is seemingly a hybrid of a mammal and reptilian creature."

    txt = txt.lower()
    scr = reading_difficulty(txt)
    print(scr)

