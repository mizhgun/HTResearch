from HTResearch.Utilities.url_tools import UrlUtility

class SmallOrganization(object):

    def __init__(self, org_model, id):
        self.id = id
        self.page_rank_info = org_model.page_rank_info
        self.org_domain = UrlUtility.get_domain(org_model.organization_url)
