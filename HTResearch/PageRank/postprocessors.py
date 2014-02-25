import numpy

from HTResearch.DataAccess.dto import OrganizationDTO
from HTResearch.DataModel.model import Organization
from HTResearch.Utilities.converter import DTOConverter

class PageRankPostprocessor(object):

    def __init__(self):
        # Injected dependencies
        self.org_dao = None

    def give_orgs_ranks(self, small_orgs, weights):
        """Assign orgs ranks and weights from vector."""
        weight_count = len(weights)

        # sanity check
        if len(small_orgs) != weight_count:
            raise Exception('Length of eigenvector does not equal number of orgs.')

        # assign page_rank_weights
        for i in range(0, weight_count):
            # Convert to native python type while we're at it
            small_orgs[i].page_rank_weight = numpy.asscalar(weights[i])

        # sort by weights
        small_orgs.sort(key=lambda x: x.page_rank_weight, reverse=True)

        # assign page_ranks
        for i in range(0, weight_count):
            small_orgs[i].page_rank = i

        return small_orgs

    def store_organizations(self, small_orgs):
        """Store small_orgs to database"""
        org_dtos = []

        # create list of dtos
        for i in range(0, len(small_orgs)):
            org_model = self._small_org_to_org_model(small_orgs[i])
            org_dto = DTOConverter.to_dto(OrganizationDTO, org_model)
            org_dto.id = small_orgs[i].id
            org_dtos.append(org_dto)

        # store
        self.org_dao.page_rank_store(org_dtos)

    def _small_org_to_org_model(self, small_org):
        return Organization(page_rank=small_org.page_rank, page_rank_info=small_org.page_rank_info,
                            page_rank_weight=small_org.page_rank_weight)