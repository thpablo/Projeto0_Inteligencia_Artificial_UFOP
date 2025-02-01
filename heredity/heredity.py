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


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
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

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
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
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def parent_prob(num_genes):
        pass_gene = num_genes / 2
        return pass_gene * (1 - PROBS["mutation"]) + (1 - pass_gene) * PROBS["mutation"]

def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.
    """
    prob = 1.0
    for person in people:
        quant_genes = 1 if person in one_gene else 2 if person in two_genes else 0
        trait_status = person in have_trait

        if people[person]['mother'] is None:
            gene_prob = PROBS['gene'][quant_genes]
            prob *= gene_prob * PROBS['trait'][quant_genes][trait_status]
        else:
            mother = people[person]['mother']
            father = people[person]['father']

            # Determine parents' gene counts
            mother_genes = 1 if mother in one_gene else 2 if mother in two_genes else 0
            father_genes = 1 if father in one_gene else 2 if father in two_genes else 0

            # Probability of passing a gene considering mutation
            prob_mother = parent_prob(mother_genes)
            prob_father = parent_prob(father_genes)

            # Calculate the probability for the child's gene count
            if quant_genes == 0:
                p = (1 - prob_father) * (1 - prob_mother)
            elif quant_genes == 1:
                p = (1 - prob_father) * prob_mother + prob_father * (1 - prob_mother)
            elif quant_genes == 2:
                p = prob_father * prob_mother
            else:
                p = 0

            prob *= p * PROBS['trait'][quant_genes][trait_status]

    return prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        ## Check how many genes the person has
        quant_genes = 1 if person in one_gene else 2 if person in two_genes else 0

        ## Check if person has trait
        trait_status = False
        if person in have_trait:
            trait_status = True

        probabilities[person]['gene'][quant_genes] += p
        probabilities[person]['trait'][trait_status] += p

    return probabilities

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for person in probabilities:
        total_genes = sum(probabilities[person]['gene'].values())
        total_trait = sum(probabilities[person]['trait'].values())

        for gene in probabilities[person]['gene']:
            probabilities[person]['gene'][gene] = probabilities[person]['gene'][gene] / total_genes
        for trait in probabilities[person]['trait']:
            probabilities[person]['trait'][trait] = probabilities[person]['trait'][trait] / total_trait

    return


if __name__ == "__main__":
    main()
