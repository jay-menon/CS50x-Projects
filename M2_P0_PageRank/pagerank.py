import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    # Call crawl on one of the directories corpus0/1/2 which parses it and outputs corpus dictionary
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    # os.listdir(directory) returns a list of strings if all the filenames in the arg directory
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        # For html files, open that given html file as f:
        with open(os.path.join(directory, filename)) as f:
            # Read the contents, find the links and put the links as values for the page that was just read
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            # Make sure that the value pages do not include the definition page - prevents self-referencing
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    # Currently the script above finds ALL links that a page links to but we're only interested in the links to pages that
    # we can find the next links for (i.e. pages in the corpus)
    # Hence this script removes all values that are not also definitions in the pages dictionary
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    N = len(corpus)
    prob_dict = {comp_page:(1-damping_factor)*(1/N) for comp_page in corpus}
    num_links = len(corpus[page])
    if num_links != 0:
        for comp_page in corpus[page]:
            prob_dict[comp_page] += damping_factor*(1/num_links)
    else:
        for comp_page in corpus[page]:
            prob_dict[comp_page] += damping_factor*(1/N)
    return prob_dict
    raise NotImplementedError

def wheel_spin(prob_dist):
    rand_int = random.randrange(1,1001)
    lb = 0
    for page in prob_dist:
        ub = lb + prob_dist[page]*1000
        if rand_int >= lb and rand_int <= ub:
            return page
        else:
            lb = ub
    return None

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    freq_dict = {page:0 for page in corpus}
    curr_page = list(corpus)[random.randrange(0, len(corpus))]
    for i in range(0, n):
        prob_dist = transition_model(corpus, curr_page, damping_factor)
        next_page = wheel_spin(prob_dist)
        curr_page = next_page
        freq_dict[curr_page] += 1
    for page in freq_dict:
        freq_dict[page] = freq_dict[page]/n
    return freq_dict
    raise NotImplementedError


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Corpus correction
    corrected_corpus = dict(corpus)
    for page in corpus:
        if corpus[page] == set():
            corrected_corpus[page] = set(corpus)

    # Initialise page ranking
    N = len(corrected_corpus)
    curr_prob_dict = {page:1/N for page in corrected_corpus}
    convergence = False

    while not convergence:
        
        old_dict = {page:round(curr_prob_dict[page], 3) for page in curr_prob_dict}
        for page in curr_prob_dict:
            sum = 0
            for comp_page in corrected_corpus:
                if page in corrected_corpus[comp_page]:
                    sum += curr_prob_dict[comp_page]/len(corrected_corpus[comp_page])
    
            # Calculate new probability and update dictionary
            new_prob = (1-damping_factor)*(1/N) + (damping_factor)*sum

            curr_prob_dict[page] = new_prob

        # Normalise dict
        sum = 0
        for page in curr_prob_dict:
            sum += curr_prob_dict[page]
        for page in curr_prob_dict:
            curr_prob_dict[page] = curr_prob_dict[page]/sum

        new_dict = {page:round(curr_prob_dict[page], 3) for page in curr_prob_dict}
        if old_dict == new_dict:
            convergence = True
    return new_dict
    raise NotImplementedError


if __name__ == "__main__":
    main()




# NOTES:
# In the random surfer model, do we allow the CURRENT page to be an option in the cases where:
    # we make link move but page has no links so next link can be any page - YES
    # we are make random move and so next page can be any page - YES
    # we treat linkless pages as having link to all, including itself

# Do we iterate through the dictionary and recalculate every time
# Also do we re-normalise after every page iteration or after every dictionary iteration