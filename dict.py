"""
    simple google dictionary in python
"""
from __future__ import print_function
from __future__ import unicode_literals
import sys
import re
from urllib2 import urlopen, URLError
from ast import literal_eval
reload(sys)
sys.setdefaultencoding('utf8')

_COLOR = {
    # refrence  : http       : //en.wikipedia.org/wiki/ANSI_escape_code
    'bold'      : "\033[1m",
    'underline' : "\033[4m",
    'blink'     : "\033[5m",
    'reverse'   : "\033[7m",
    'concealed' : "\033[8m",

    'black'     : "\033[30m",
    'red'       : "\033[31m",
    'green'     : "\033[32m",
    'yellow'    : "\033[33m",
    'blue'      : "\033[34m",
    'magenta'   : "\033[35m",
    'cyan'      : "\033[36m",
    'white'     : "\033[37m",
    'd_black'   : "\033[30;2m",
    'd_red'     : "\033[31;2m",
    'd_green'   : "\033[32;2m",
    'd_yellow'  : "\033[33;2m",
    'd_blue'    : "\033[34;2m",
    'd_magenta' : "\033[35;2m",
    'd_cyan'    : "\033[36;2m",
    'd_white'   : "\033[37;2m",

    'on_black'   : "\033[40m",
    'on_red'     : "\033[41m",
    'on_green'   : "\033[42m",
    'on_yellow'  : "\033[43m",
    'on_blue'    : "\033[44m",
    'on_magenta' : "\033[45m",
    'on_cyan'    : "\033[46m",
    'on_white'   : "\033[47m",

    'beep': "\007",
}

TERM_FORMAT = {
    'none'     : "",
    'close'    : "\033[0m",
    'headword' : _COLOR['bold'],
    'related'  : _COLOR['d_white'],
    'example'  : _COLOR['underline'],
    'synonym'  : _COLOR['blue'],
    'index': _COLOR['red']
}
OPTIONS = {}

def fmt_text(text, fmt='none'):
    """fmt_text(text, fmt) -> string
    """
    if OPTIONS.get('no_fmt') or not TERM_FORMAT.has_key(fmt):
        return text
    return '%s%s%s'% (TERM_FORMAT[fmt], text, TERM_FORMAT['close'])


def print_def(word):
    """format definition of word
    """
    if not word:
        return
    definition = get_def(word)
    definition = format_output(definition)
    print("Definition for %s:\n %s" % (word, definition))


def get_def(word):
    """get definition from google dictionary api
    """
    goo_dict = 'http://www.google.com/dictionary/json'
    goo_dict += '?callback=s&q={query}&sl=en&tl=en&restrict=pr,de&client=te'
    url = goo_dict.format(query=word)
    definition = ''
    try:
        def_source = urlopen(url)
        definition = def_source.read()[2:-10]
    except URLError as err:
        print('Error in open url')
        print(err)
    else:
        print('what')
    finally:
        #explicitly close it
        def_source.close()

    # strip unused token
    # RE is slow
    return literal_eval(definition)


def terms(term_list, ent_type):
    """terms(term_list, ent_type) -> string
    convert terms into beautiful string
    """
    ret = []
    separator = ''

    if ent_type == 'meaning':
        separator = '\n'
        ret = [term['text'] for term in term_list]
    elif ent_type == 'related':
        separator = ', '
        for term in term_list:
            label = term.get('labels', [{}])[0]
            label = label.get('text', '')
            text = '%s %s'% (term['text'], fmt_text(label, 'related'))
            ret.append(text)
    elif ent_type == 'example':
        separator = '\n'
        repl = lambda t: fmt_text(t.group(1), 'example')
        for term in term_list:
            text = term['text']
            text = re.sub(r'<em>(.*?)</em>', repl, text)
            ret.append(' '*4 + text)
    elif ent_type == 'headword':
        word = term_list[0]
        text = '\n' + fmt_text(word['text'], 'headword')
        ret.append(text)
        ret.append(' '+word['labels'][0]['text'])
        term_list = term_list[1:]
        separator = ' | '
        ret.extend([term['text'] for term in term_list\
                if term['type'] != 'sound'])
    elif ent_type == 'synonym':
        separator = ', '
        ret = [term['text'] for term in term_list]

    return separator.join(ret)


def entry(ent, index=0):
    """entry(ent, index=0) -> string
    ent is a dict has 3 keys:
        'type': string
        'terms': <term_list>
            term:
                type: string
                text: string
                language: string
                [labels]: <dict>
        'entries': <entry_list>
    """
    ret = []
    ent_type = ent.get('type', '')
    term_list = ent.get('terms', [])
    term_text = terms(term_list, ent_type)
    if ent_type == 'meaning' and index:
        term_text = '  {0}: {1}'.format(\
                fmt_text(str(index), 'index'),  term_text)
    ret.append(term_text)
    entries = ent.get('entries', [])
    if ent_type == 'synonym':
        label = ent['labels'][0]['text']
        ret.append(fmt_text(label+': ', 'synonym'))
    for num, child in enumerate(entries):
        if ent_type == 'synonyms':
            child['type'] = 'synonym'
        ret.append(entry(child, num))
    return '\n'.join(ret)



def format_output(dfn):
    """format_output(definition) -> string
    """
    ret = []
    if 'primaries' in dfn:
        ret.extend([entry(ent) for ent in dfn['primaries']])
    if 'synonyms' in dfn:
        for ent in dfn['synonyms']:
            ent['type'] = 'synonym'
            ret.append(entry(ent))

    return ''.join(ret)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for w in sys.argv[1:]:
            print_def(w)

    else :
        while True:
            try:
                print_def(raw_input('Enter word: \n'))
            except (EOFError, KeyboardInterrupt):
                print("Bye")
                exit(0)
