import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
S -> NP VP NP
S -> NP VP PP
S -> S Conj S
S -> S Adv
S -> S Conj VP

NP -> N | Det N
NP -> NP PP
NP -> Det AdjP

PP -> P NP

VP -> V | Adv V
VP -> VP NP

AdjP -> Adj NP | Adj AdjP
"""

ALPHABET = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
            "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    
    # Cleans sentence and separates words by spaces between them
    clean_sentence = sentence.strip("\n").strip(".")
    sentence_list = clean_sentence.split(" ")

    # Lowercases all words and ignores items without letters
    new_sentence_list = []
    for item in sentence_list:
        
        # Filters out nay punctuation-only items
        if item.upper() != item.lower():

            # Filters out any punctuation in items with letters
            new_word = ""
            for character in item.lower():
                if character in ALPHABET:
                    new_word += character
            new_sentence_list.append(new_word)        

    # Returns new_sentence_list
    return new_sentence_list


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """

    np_chunks = []

    for subtree in tree.subtrees():
        label = subtree.label()
        np_subtrees = [i for i in subtree.subtrees(filter=lambda x: x.label() == "NP")]

        if label == "NP" and len(np_subtrees) == 1:
            np_chunks.append(subtree)
    
    return np_chunks


if __name__ == "__main__":
   main()



# t = nltk.Tree.fromstring("(S (NP (D the) (N dog)) (VP (V chased) (NP (D the) (N cat))))")
# for i in t.subtrees():
#     print(i)