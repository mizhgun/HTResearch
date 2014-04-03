#
# app.py
# An executable script for running the PageRank algorithm.
#

# stdlib imports
import sys
from springpython.context import ApplicationContext

# project imports
from HTResearch.PageRank.algorithms import *
from HTResearch.Utilities.context import PageRankContext

if __name__ == '__main__':
    ctx = ApplicationContext(PageRankContext())
    pre = ctx.get_object('PageRankPreprocessor')
    post = ctx.get_object('PageRankPostprocessor')

    # no user input
    user_input = False

    try:
        sys.argv.index('-f')
    except Exception:
        user_input = True

    if user_input:
        # Grab some user input so they know what's up
        print 'We will perform PageRank calculations on the organizations in the database specified by' \
              ' htconfig.cfg. Please ensure no spiders are running to avoid information being overwritten.' \
              'It is also probably smart to backup the database beforehand.\n'

        proceed = raw_input('Enter y to proceed. Any other character(s) will exit: ').upper() == 'Y'
        if not proceed:
            sys.exit()

    print 'Bring organizations to memory'
    orgs = pre.bring_orgs_to_memory()

    print 'Cleaning organizations'
    orgs = pre.cleanup_data(orgs)

    print 'Creating matrix'
    matrix = pre.create_matrix(orgs)

    print 'Creating the dampened google matrix'
    matrix = google_matrix(matrix)

    print 'Generating eigenvector'
    vector = left_eigenvector(matrix)

    print 'Assigning ranks to organizations'
    orgs = post.give_orgs_ranks(orgs, vector)

    print 'Storing organizations'
    post.store_organizations(orgs)

    print 'Complete!'
