"""simple spell checker"""
from os.path import isfile

DICT = [d for d in ('/Usr/dict/words', '/Usr/share/dict/words') if isfile(d)]
VOCAB = []
ALPHA = [chr(j) for j in xrange(97, 123)]

if DICT:
    VOCAB = open(DICT[0]).read().lower().split('\n')
    VOCAB = dict((w, 1) for w in set(VOCAB))


def edit1(word):
    """return set of words whose levenshtein distance is 1 from word
        The first letter must be same"""
    split = [(word[:i], word[i:]) for i in range(1, len(word)+1)]
    insert = [a + c + b for c in ALPHA for a, b in split]
    delete = [a + b[1:] for a, b in split if b]
    replace = [a + c + b[1:] for c in ALPHA for a, b in split if b]
    swap = [a + b[1] + b[0] + b[2:] for a, b in split if len(b) > 1]
    return set(delete + swap + replace + insert)

def edit2(word):
    """return set of words whose levenshtein distance is 2 from word"""
    return set(e2 for e1 in edit1(word) for e2 in edit1(e1))

def known(words):
    """only words in dictionary"""
    return set(w for w in words if w in VOCAB)

def correct(word):
    """get candidate"""
    if not VOCAB:
        return []
    word = word.lower()
    return known(edit1(word)) or known(edit2(word))

if __name__ == '__main__':
    print(correct('maening'))
