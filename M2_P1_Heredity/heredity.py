import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}

PASSDOWN_PROBS = {
    # Given number of genes parent has:
    0:{
        # What is the probability of passing down 0 or 1 of the gene
        0: 1 - PROBS["mutation"],
        1: PROBS["mutation"]
    },
    1:{
        0: 0.5,
        1: 0.5
    },
    2:{
        0: PROBS["mutation"],
        1: 1 - PROBS["mutation"]
    }
}

def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    # Records all information from csv into dictionary called people
    # Use people[person_name][csv_col_name] to access that data
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person in probabilities dictionary
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information: ignore that potential subset if it does
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # If subset make it to here, all the people in that subset could have the gene
        # Nested for loops iterate over all possible gene arrangements of the people in the gene-havers subset
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s, including the empty set.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # Organise initial information
    parent_dict = {}
    child_dict = {}
    child_parent_dict = {}
    indv_probs = []
    for person in people:
        # Find person's gene number in this model
        if person in one_gene:
            gene_num = 1
        elif person in two_genes:
            gene_num = 2
        else:
            gene_num = 0
        # Find person's trait status in this model
        if person in have_trait:
            trait = True
        else:
            trait = False
        # Find out if person is child or parent in this model and add all info to dictionaries
        if not people[person]["mother"] and not people[person]["father"]:
            parent_dict[person] = [gene_num, trait]
            # Calculate parent probabilities as they are unconditional
            [gene_prob, trait_prob] = parent_prob(gene_num, trait)
            indv_probs.append(gene_prob*trait_prob)
        else:
            child_dict[person] = [gene_num, trait]
            child_parent_dict[person] = [people[person]["mother"], people[person]["father"]]

    # Calculate child probabilities:
    for child in child_dict:
        [gene_prob, trait_prob] = child_prob(child_dict[child], parent_dict[child_parent_dict[child][0]], parent_dict[child_parent_dict[child][1]])
        indv_probs.append(gene_prob*trait_prob)

    # Calculate overall joint probability:
    joint_prob = indv_probs[0]
    for prob in indv_probs[1:]:
        joint_prob *= prob

    return joint_prob


def parent_prob(gene_num, trait):
    
    prob = [None,None]
    prob[0] = PROBS["gene"][gene_num]
    if trait:
        prob[1] = PROBS["trait"][gene_num][True]
    else:
        prob[1] = PROBS["trait"][gene_num][False]
    return prob


def child_prob(child_status, mum_status, dad_status):

    # Model gene scenarios that could result in child having gene_num
    gene_prob = 0
    # for mut_mum in [-1,0,1]:
    #     for mut_dad in [-1,0,1]:
    #         if (mum_status[0] + mut_mum <= 0 or mum_status[0] + mut_mum >= 3) or (dad_status[0] + mut_dad <= 0 or dad_status[0] + mut_dad >= 3):
    #             continue
    #         elif mum_status[0] + mut_mum + dad_status[0] + mut_dad == child_status[0]:
    #             non_mutated = [mut_mum, mut_dad].count(0)
    #             if non_mutated == 0:
    #                 gene_prob += (1 - PROBS["mutation"])*(1 - PROBS["mutation"])
    #             elif non_mutated == 1:
    #                 gene_prob += (1 - PROBS["mutation"])*(PROBS["mutation"])
    #             else:
    #                 gene_prob += (PROBS["mutation"])*(PROBS["mutation"])

    for mum_passdown in [0,1]:
        for dad_passdown in [0,1]:
            if mum_passdown + dad_passdown == child_status[0]:
                gene_prob += PASSDOWN_PROBS[mum_status[0]][mum_passdown] * PASSDOWN_PROBS[dad_status[0]][dad_passdown] 
    # Model trait stuff
    if child_status[1]:
        trait_prob = PROBS["trait"][child_status[0]][True]
    else:
        trait_prob = PROBS["trait"][child_status[0]][False]
    return [gene_prob, trait_prob]


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in one_gene:
        probabilities[person]["gene"][1] += p
    for person in two_genes:
        probabilities[person]["gene"][2] += p
    for person in (set(probabilities) - (two_genes | one_gene)):
        probabilities[person]["gene"][0] += p
    for person in have_trait:
        probabilities[person]["trait"][True] += p
    for person in (set(probabilities) - have_trait):
        probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # Sum all non-normalised probabilities for each person's gene/trait distribution
    for person in probabilities:
        gene_sum = 0
        trait_sum = 0
        for gene_count in probabilities[person]["gene"]:
            gene_sum += probabilities[person]["gene"][gene_count]
        for trait_status in probabilities[person]["trait"]:
            trait_sum += probabilities[person]["trait"][trait_status]
        # Normalise probabilities relative to that sum
        for gene_count in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene_count] = probabilities[person]["gene"][gene_count]/gene_sum
        for trait_status in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait_status] = probabilities[person]["trait"][trait_status]/trait_sum


if __name__ == "__main__":
    main()
