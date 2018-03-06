import libtcodpy as libtcod
import re
from textwrap import wrap
from pyro.settings import MSG_WIDTH, MSG_HEIGHT


class Pronoun:
    class _Pronoun:
        def __init__(self, subjective, objective, possessive):
            self.subjective = subjective
            self.objective = objective
            self.possessive = possessive

    YOU = _Pronoun('you', 'you', 'your')
    SHE = _Pronoun('she', 'her', 'her')
    HE = _Pronoun('he', 'him', 'his')
    IT = _Pronoun('it', 'it', 'its')
    THEY = _Pronoun('they', 'them', 'their')


class Noun:
    def noun_text(self):
        return None

    def pronoun(self):
        return Pronoun.IT

    def __str__(self):
        return self.noun_text()


class LogType:
    MESSAGE = 'message'
    ERROR = 'error'
    # TODO more log types for different appearances


class Message:
    def __init__(self, type_, text):
        """LogType, text, and number of times this message has been repeated."""
        self.type = type_
        self.text = text
        self.count = 1


class Log:
    def __init__(self, messages=None):
        self.messages = messages or []

    def message(self, text, color=libtcod.white, type_=LogType.MESSAGE):
        # Split the message if necessary, among multiple lines
        new_msg_lines = wrap(text, MSG_WIDTH)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room
            if len(self.messages) == MSG_HEIGHT:
                del self.messages[0]

            # Add the new line as a tuple, with the text and color
            message = Message(type_, line)
            self.messages.append((message, color))

    def message2(self, message, noun1=None, noun2=None, noun3=None):
        # TODO self.add(LogType.MESSAGE, message, noun1, noun2, noun3)
        self.message(_format(message, noun1, noun2, noun3),
                     color=None, type_=LogType.MESSAGE)

    def error(self, message, noun1=None, noun2=None, noun3=None):
        # TODO self.add(LogType.ERROR, message, noun1, noun2, noun3)
        self.message(_format(message, noun1, noun2, noun3),
                     color=None, type_=LogType.ERROR)

    # def add(self, type_, message, noun1=None, noun2=None, noun3=None):
    #     message = _format(message, noun1, noun2, noun3)
    #
    #     # See if it's a repeat of the last message
    #     if len(self.messages) > 0:
    #         last = self.messages[len(self.messages) - 1]
    #         if last.text == message:
    #             last.count += 1
    #             return
    #
    #     # It's a new message
    #     self.message(message, color=None, type_=type_)
    #     # TODO implement max number of messages?


def _format(text, noun1=None, noun2=None, noun3=None):
    """
    The same message can apply to a variety of subjects and objects, and it
    may use pronouns of various forms. For example, a hit action may want to
    be able to say:
     
        * You hit the troll with your sword.
        * The troll hits you with its club.
        * The mermaid hits you with her fin.
        
    To avoid handling of these cases at each message site, we use a simple
    formatting DSL that can handle pronouns, subject/verb agreement, etc.
    This function takes a format string and a series of nouns (numbered from
    1 through 3) and creates an appropriate cases and tensed string.
    
    The following formatting is applied:
    
    ### Nouns: `{#}`
    
    A number inside curly braces expands to the name of that noun. For
    example, if noun 1 is a bat then `{1}` expands to `the bat`.
    
    ### Subjective pronouns: `{# he}`
    
    A number in curly braces followed by `he` (with a space between)
    expands to the subjective pronoun for that noun. It takes into account
    the noun's person and gender. For example, if noun 2 is a mermaid then
    `{2 he}` expands to `she`.
    
    ### Objective pronouns: `{# him}`
    
    A number in curly braces followed by `him` (with a space between)
    expands to the objective pronoun for that noun. It takes into account
    the noun's person and gender. For example, if noun 2 is a jelly then
    `{2 him}` expands to `it`.
    
    ### Possessive pronouns: `{# his}`
    
    A number in curly braces followed by `his` (with a space between)
    expands to the possessive pronoun for that noun. It takes into account
    the noun's person and gender. For example. if noun 2 is a mermaid then
    `{2 his}` expands to `her`.
    
    ### Regular verbs: `[suffix]`
    
    A series of letters enclosed in square brackets defines an optional verb
    suffix. If noun 1 is second person, then the contents will be included.
    Otherwise they are omitted. For example, `open[s]` will result in `open`
    if noun 1 is second-person (i.e. the Hero) or `opens` if third-person.
    
    ### Irregular verbs: `[second|third]`
    
    Two words in square brackets separated by a pipe (`|`) defines an
    irregular verb. If noun 1 is second person then the first word is used,
    otherwise the second is. For example, `[are|is]` will result in `are` if
    noun 1 is second-person (i.e. the Hero) or `is` if third-person.
    
    ### Sentence case
    
    Finally, the first letter in the result will be capitalized to properly
    sentence case it.
    """
    result = text

    nouns = [noun1, noun2, noun3]
    for i in range(1, 4):
        noun = nouns[i - 1]
        if noun:
            result = result.replace('{%d}' % i, noun.noun_text())

            # Handle pronouns
            result = result.replace('{%d he}' % i, noun.pronoun().subjective)
            result = result.replace('{%d him}' % i, noun.pronoun().objective)
            result = result.replace('{%d his}' % i, noun.pronoun().possessive)

    # Make the verb match the subject (which is assumed to be the first noun)
    if noun1:
        result = _conjugate(result, noun1.pronoun())

    # Sentence case it by capitalizing the first letter
    return result.capitalize()


def _conjugate(text, pronoun):
    first = pronoun == Pronoun.YOU or pronoun == Pronoun.THEY
    return _categorize(text, first)


_RE_OPTIONAL_SUFFIX = re.compile(r"\[(\w+?)\]")
_RE_IRREGULAR = re.compile(r"\[([^|]+)\|([^\]]+)\]")


def _categorize(text, first, force=False):
    """
    Parses a string and chooses one of two grammatical categories.
    
    If used for verbs, selects a verb form to agree with a subject. In that 
    case, the first category is for agreeing with a third-person singular
    noun ("it runs") and the second is for a second-person noun ("you run").
    
    If used for a noun, selects a number. The first category is singular
    ("knife") and the second is plural ("knives").
    
    Examples:
        
        _categorize("run[s]", first=True)       => "run"
        _categorize("run[s]", first=False)      => "runs"
        _categorize("bunn[y|ies]", first=True)  => "bunny"
        _categorize("bunn[y|ies]", first=False) => "bunnies"
    
    If force is true, then a trailing 's' will be added to the end if
    first is false and text doesn't have any formatting.
    """
    # If it's a regular word in second category, just add an 's'
    if force and not first and "[" not in text:
        return "{}s".format(text)

    # Handle words with optional suffices like `close[s]` and `sword[s]`
    while True:
        match = _RE_OPTIONAL_SUFFIX.search(text)
        if match is None:
            break

        before = text[0:match.start()]
        after = text[match.end():]
        if first:
            # Omit the optional part
            text = '%s%s' % (before, after)
        else:
            # Include the optional part
            text = '%s%s%s' % (before, match.group(1), after)

    # Handle irregular words like `[are|is]` and `sta[ff|aves]`
    while True:
        match = _RE_IRREGULAR.search(text)
        if match is None:
            break

        before = text[0:match.start()]
        after = text[match.end():]
        if first:
            # Use the first form
            text = '%s%s%s' % (before, match.group(1), after)
        else:
            # Use the second form
            text = '%s%s%s' % (before, match.group(2), after)

    return text


def quantify(text, count):
    """
    Quantifies the noun pattern in [text] to create a noun phrase for that
    number. Examples:
    
        quantify("bunn[y|ies]", 1) => "a bunny"
        quantify("bunn[y|ies]", 2) => "2 bunnies"
        quantify("(a) unicorn", 1) => "a unicorn"
        quantify("ocelot", 1)      => "an ocelot"
    """
    if count == 1:
        # Handle irregular nouns that start with a vowel but use "a",
        # like "a unicorn"
        if text.startswith('(a) '):
            quantity = 'a'
            text = text[4:]
        elif text[0] in 'aeiou':
            quantity = 'an'
        else:
            quantity = 'a'
    else:
        quantity = '%d' % count
    return '%s %s' % (quantity, _categorize(text, first=count == 1, force=True))
