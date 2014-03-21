#
# helper_classes.py
# A module containing classes useful to any stage in the PageRank process.
#

# project imports
from HTResearch.Utilities.url_tools import UrlUtility

class SmallOrganization(object):
    """
    A smaller version of the Organization object with only the fields necessary for the PageRank algorithm.

    Attributes:
        id (ObjectId): ID of the OrganizationDTO in the database.
        page_rank_info (PageRankInfo): The organization's page rank information.
        org_domain (string): String of the organizations domain.
        page_rank (long): Organization's ranking by page weight where 0 is the most highly rated. None or 2^63 - 1 if
            not ranked.
        page_rank_weight (float): Organization's PageRank weight between 0.0 and 1.0 where 1.0 is most highly weighted.
    """

    def __init__(self, org_model, id):
        """
        Constructs a new SmallOrganization instance.

        Arguments:
            org_model (Organization): The organization from which to create a SmallOrganization.
            id (ObjectId): The database ID of the organization.
        """
        self.id = id
        self.page_rank_info = org_model.page_rank_info
        try:
            self.org_domain = UrlUtility.get_domain(org_model.organization_url, no_exception=False)
        except Exception:
            self.org_domain = None
        self.page_rank = None
        self.page_rank_weight = None
