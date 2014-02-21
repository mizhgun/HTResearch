from HTResearch.Utilities.url_tools import UrlUtility

class SmallOrganization(object):

    def __init__(self, org_model, id):
        self.id = id
        self.page_rank_info = org_model.page_rank_info
        try:
            self.org_domain = UrlUtility.get_domain(org_model.organization_url, no_exception=False)
        except Exception:
            self.org_domain = None
        self.page_rank = None
        self.page_rank_weight = None
