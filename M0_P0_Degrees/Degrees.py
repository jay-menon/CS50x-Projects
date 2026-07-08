# Module 0: Search
# Project 0: Degrees
# Program finds degrees of social separation between 2 actors on imdb

import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass

def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python Degrees.py [csv_directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]

def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    initial_node = Node(source, None, neighbors_for_person(source))
    frontier = QueueFrontier()
    frontier.add(initial_node)
    visited_actor_IDs = {source}
    while frontier.empty() is False:
        if frontier.contains_state(target):
            final_node = search_frontier(frontier, target)
            path = path_retracer(final_node, source)
            return path
        else:
            curr_node = frontier.remove()
            visited_actor_IDs.add(curr_node.state)
            for connection in curr_node.action:
                if connection[1] not in visited_actor_IDs:
                    visited_actor_IDs.add(connection[1])
                    frontier.add(Node(connection[1], [connection[0], curr_node], neighbors_for_person(connection[1])))
    return None

def search_frontier(frontier, target):
    for node in frontier.frontier:
        if node.state == target:
            return node

def path_retracer(final_node, source):
    path = []
    curr_node = final_node
    while curr_node.state != source:
        path.insert(0,[curr_node.parent[0], curr_node.state])
        curr_node = curr_node.parent[1]
    return path

def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors

if __name__ == "__main__":
    main()

# Problems to fix:
# 1. Duplicate actors in the frontier
# 2. Not using the class methods and instead, manually exectuing them
# 3. Node.parent currently contains the whole history of previous nodes (should only contain the previous one)
# 4. Change already explored actor list to a SET: faster search and .add automatically avoids duplicates
    # A value going into a set will have the same associated hash every time and so when we try add an item to a set,
    # the system only needs to check if that hash slot has already been occupied or not
# 5. Action is not used as intended either: the action for a node ought to be the movie_ID that links the current node to the parent one
# NOTE: We used list for frontier over a set because ORDER MATTERS for the frontier    