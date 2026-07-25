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
    prob_int = random.randrange(1, 101)
    if prob_int <= int(damping_factor/100):
        page_list = list(corpus[page])
    else:
        page_list = list(set(corpus)-{page})
    rand_idx = random.randrange(0, len(page_list))
    next_page = page_list[rand_idx]
    return next_page
    raise NotImplementedError


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
        next_page = transition_model(corpus, curr_page, damping_factor)
        curr_page = next_page
        freq_dict[curr_page] += 1
    print(freq_dict)
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
    N = len(corpus)
    curr_prob_dict = {page:1/N for page in corpus}
    curr_page = list(corpus)[random.randrange(0, len(corpus))]
    convergence = False
    while not convergence:
        next_page = transition_model(corpus, curr_page, damping_factor)
        sum = 0
        for page in corpus:
            if next_page in corpus[page]:
                sum += curr_prob_dict[page]/len(corpus[page])

        # Calculate new probability and update dictionary
        #PR(p) = d(1/N) + (1-d)sum(PR(i)/num(i))
        new_prob = damping_factor*(1/N) + (1-damping_factor)*sum
        new_prob_dict = dict(curr_prob_dict)
        new_prob_dict[next_page] = new_prob

        # Check for convergence
        round_curr_dict = {page:round(curr_prob_dict[page], 4) for page in curr_prob_dict}
        round_next_dict = {page:round(new_prob_dict[page], 4) for page in new_prob_dict}
        if round_curr_dict == round_next_dict:
            convergence = True
        curr_page = next_page
        curr_prob_dict = round_next_dict

    # Normalise probability dictionary
    sum = 0
    for page in curr_prob_dict:
        sum += curr_prob_dict[page]

    for page in curr_prob_dict:
        curr_prob_dict[page] = curr_prob_dict[page]/sum

    return curr_prob_dict
    raise NotImplementedError


if __name__ == "__main__":
    main()
