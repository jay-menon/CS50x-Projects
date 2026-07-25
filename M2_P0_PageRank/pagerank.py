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
    raise NotImplementedError


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
