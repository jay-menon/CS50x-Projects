import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4
MONTH_DICT = {
    "Jan": 0,
    "Feb": 1,
    "Mar": 2,
    "Apr": 3,
    "May": 4,
    "June": 5,
    "Jul": 6,
    "Aug": 7,
    "Sep": 8,
    "Oct": 9,
    "Nov": 10,
    "Dec": 11
}

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    # Open and do an initial clean of csv data
    with open(filename) as csv:
        raw_list = csv.readlines()
    string_list = [item.strip("\n").split(",") for item in raw_list[1:]]

    # Final clean of data, separating columns into evidence and labels
    evidence = []
    labels = []
    for data in string_list:

        # Collect the evidence in the required format for each datapoint
        new_evidence = [None] * 17
        # - Administrative, an integer
        new_evidence[0] = int(data[0])
        # - Administrative_Duration, a floating point number
        new_evidence[1] = float(data[1])
        # - Informational, an integer
        new_evidence[2] = int(data[2])
        # - Informational_Duration, a floating point number
        new_evidence[3] = float(data[3])
        # - ProductRelated, an integer
        new_evidence[4] = int(data[4])
        # - ProductRelated_Duration, a floating point number
        new_evidence[5] = float(data[5])
        # - BounceRates, a floating point number
        new_evidence[6] = float(data[6])
        # - ExitRates, a floating point number
        new_evidence[7] = float(data[7])
        # - PageValues, a floating point number
        new_evidence[8] = float(data[8])
        # - SpecialDay, a floating point number
        new_evidence[9] = float(data[9])
        # - Month, an index from 0 (January) to 11 (December)
        new_evidence[10] = MONTH_DICT[data[10]]
        # - OperatingSystems, an integer
        new_evidence[11] = int(data[11])
        # - Browser, an integer
        new_evidence[12] = int(data[12])
        # - Region, an integer
        new_evidence[13] = int(data[13])
        # - TrafficType, an integer
        new_evidence[14] = int(data[14])
        # - VisitorType, an integer 0 (not returning) or 1 (returning)
        if data[15] == "Returning_Visitor":
            new_evidence[15] = 1
        else:
            new_evidence[15] = 0
        # - Weekend, an integer 0 (if false) or 1 (if true)
        if data[16] == "TRUE":
            new_evidence[16] = 1
        else:
            new_evidence[16] = 0

        # Format the label in the required format
        if data[17] == "TRUE":
            new_label = 1
        else:
            new_label = 0

        # Add both to evidence/labels list
        evidence.append(new_evidence)
        labels.append(new_label)

    # Return correctly formatted evidence and labels lists
    return evidence, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model
    raise NotImplementedError


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
