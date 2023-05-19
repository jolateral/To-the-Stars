"""CSC111 Project Phase 2 : Final Submission

Module Description
===============================

This Python module contains the code used to read the dataset that we got via Kaggle,
which contains information on a specific star in our galaxy.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited.

This file is Copyright (c) 2023 Janna Alyssa Lim, Jenny Nguyen
"""
import csv
from classes import *


def read_dataset(data: str) -> tuple[Galaxy, list]:
    """Read the dataset csv file and create/return a galaxy made of the stars in the data
    set. Also, create a list of the individual stars to show in pygame.
    """
    with open(data) as csv_file:
        reader = csv.reader(csv_file)

        # skip the header row
        next(reader)

        # create a new galaxy, and add the stars to it
        new_galaxy = Galaxy()

        for row in reader:
            name = row[2]
            distance = float(row[3])
            mass = float(row[4])
            radius = float(row[5])
            new_galaxy.add_star(name, distance, mass, radius)

        stars_so_far = []
        for star in new_galaxy.stars:
            stars_so_far.append(new_galaxy.stars[star])

    return new_galaxy, stars_so_far


if __name__ == '__main__':
    # This runs pytest on the tests cases you've defined in this file.
    import pytest
    pytest.main(['a1_part1.py', '-v'])

    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (In PyCharm, select the lines below and press Ctrl/Cmd + / to toggle comments.)
    # You can use "Run file in Python Console" to run both pytest and PythonTA,
    # and then also test your methods manually in the console.
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['csv'],
        'allowed-io': ['read_dataset'],
        'max-line-length': 120,
        'disable': ['invalid-name']
    })
