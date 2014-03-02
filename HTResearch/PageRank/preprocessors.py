from helper_classes import SmallOrganization
from HTResearch.DataModel.model import Organization, PageRankInfo
from HTResearch.Utilities.converter import DTOConverter
from HTResearch.Utilities.lists import index_of

class PageRankPreprocessor(object):

    def __init__(self):
        # Injected dependencies
        self.org_dao = None

    def bring_orgs_to_memory(self):
        """ Make a db call to get all organizations and trim it down to a smaller model to conserve space"""

        # grab all organizations
        tmp_org_dtos = self.org_dao.all("id", "page_rank_info.total", "organization_url",
                                        "page_rank_info.total_with_self", "page_rank_info.references.count",
                                        "page_rank_info.references.org_domain", "page_rank_info.references.pages.url",
                                        "page_rank_info.references.pages.count")

        # convert the dtos to this smaller model
        small_orgs = [SmallOrganization(DTOConverter.from_dto(Organization, o), o.id) for o in tmp_org_dtos if o.organization_url]
        small_orgs = [o for o in small_orgs if o.org_domain]

        # At this point, tmp_org_dtos gets gc'd and we're left with the minimum data needed for calculation
        return small_orgs

    def cleanup_data(self, small_orgs):
        """Make sure the counts all add up so we don't get screwed up by the math later"""

        # List of domains we care about, remove the rest
        org_domains = [o.org_domain for o in small_orgs]

        for org in small_orgs:
            if org.page_rank_info is None:
                org.page_rank_info = PageRankInfo()

            org.page_rank_info.total = 0
            org.page_rank_info.total_with_self = 0
            for i in xrange(len(org.page_rank_info.references) - 1, -1, -1):
                ref = org.page_rank_info.references[i]
                # If the domain of the reference is not in the domain of organizations, then it's a link to
                # a non-org like facebook.com so we delete it
                if not ref.org_domain in org_domains:
                    del org.page_rank_info.references[i]
                    continue

                # If here, then this is a reference to another stored org so we verify the counts
                ref.count = 0
                for page in ref.pages:
                    ref.count += page.count
                org.page_rank_info.total_with_self += ref.count
                if ref.org_domain != org.org_domain:
                    org.page_rank_info.total += ref.count

        # Sort organizations in a predictable way, b/c where they're going they won't have names
        # which means we'll need the index
        small_orgs.sort(key=lambda x: x.org_domain)

        return small_orgs

    def create_matrix(self, cleaned_small_orgs):
        """Convert the cleaned small_orgs to a matrix."""

        org_count = len(cleaned_small_orgs)

        if org_count <= 0:
            return None

        default_val = 1 / float(org_count)

        matrix = []
        for org in cleaned_small_orgs:
            # initialize row to zeros
            row = [0] * org_count

            total = 0.0

            for ref in org.page_rank_info.references:
                # don't count self for now...
                if ref.org_domain == org.org_domain:
                    continue

                # find index of the referenced organization in the list
                index = index_of(cleaned_small_orgs, lambda x: x.org_domain == ref.org_domain)
                if index != -1:
                    row[index] = ref.count / float(org.page_rank_info.total)
                    # track total to make sure this all adds to 1.0
                    total += row[index]

            # if zero, org didn't referefence other organizations,
            # set all values evenly to simulate random navigation behavior
            if total == 0.0:
                for i in range(0, org_count):
                    row[i] = default_val
                    total += default_val

            # if our total doesn't add to exactly 1.0, compensate.
            if total != 1.0:
                # first, try to distribute equally
                diff = 1.0 - total
                refs_count = len(org.page_rank_info.references)
                if refs_count == 0:
                    # set to org_count if no references
                    refs_count = org_count
                diff_to_add = diff / refs_count
                for i in range(0, org_count):
                    if row[i] != 0.0:
                        row[i] += diff_to_add
                        total += diff_to_add

                # if still not perfect, just alter the first val that's big enough to not be a huge deal
                if total != 1.0:
                    diff = 1.0 - total
                    first_val = index_of(row, lambda x: x > abs(diff_to_add))
                    row[first_val] += diff
                    total = 1.0

            # add row to matrix
            matrix.append(row)

        # sanity check
        if len(matrix) != org_count:
            raise Exception('Error: The matrix constructed is not square in preprocessors.py - create_matrix().')

        return matrix