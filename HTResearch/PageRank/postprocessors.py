#
# postprocessors.py
# A module containing helpers to organize the information from the PageRank algorithm into database models and to
# store those models.
#

# stdlib imports
import numpy

# project imports
from HTResearch.DataAccess.dto import OrganizationDTO
from HTResearch.DataModel.model import Organization
from HTResearch.Utilities.converter import DTOConverter

class PageRankPostprocessor(object):
    """
    A class to use PageRank functions. These functions are organized into a class to allow for the easy injection of
    org_daos.

    Attributes:
        org_dao (OrganizationDAO): A DAO for storing organizations
    """

    def __init__(self):
        """
        Constructs a new PageRankPostprocessor instance.
        """

        # Injected dependencies
        self.org_dao = None

    def give_orgs_ranks(self, small_orgs, weights):
        """
        Assign orgs ranks and weights from vector.

        Arguments:
            small_orgs ([SmallOrganization]): A list of SmallOrganization objects in the same order as the weights
                vector.
            weights ([float]): A list of calculate PageRank weights between 0.0 and 1.0 in the same order as the
                small_orgs list.

        Returns:
            small_orgs ([SmallOrganization]): The same list in the small_orgs argument. Weights will be assigned after
                this function to the "page_rank" member of the SmallOrganization.
        """
        weight_count = len(weights)

        # sanity check
        if len(small_orgs) != weight_count:
            raise Exception('Length of eigenvector does not equal number of orgs.')

        # assign page_rank_weights
        for i in range(0, weight_count):
            # Convert to native python type while we're at it
            small_orgs[i].page_rank_weight = numpy.asscalar(weights.real[i])

        # sort by weights
        small_orgs.sort(key=lambda x: x.page_rank_weight, reverse=True)

        # assign page_ranks
        for i in range(0, weight_count):
            small_orgs[i].page_rank = i

        return small_orgs

    def store_organizations(self, small_orgs):
        """
        Store small_orgs to database.

        Arguments:
            small_orgs ([SmallOrganization]): A list of SmallOrganization objects to be stored to the database.
        """
        org_dtos = []

        # create list of dtos
        for i in range(0, len(small_orgs)):
            org_model = self._small_org_to_org_model(small_orgs[i])
            org_dto = DTOConverter.to_dto(OrganizationDTO, org_model)
            org_dto.id = small_orgs[i].id
            org_dtos.append(org_dto)

        # store
        self.org_dao.page_rank_store(org_dtos)

        # set documents without ranks to max
        empty_dtos = self.org_dao.findmany(page_rank__exists=False)
        for dto in empty_dtos:
            dto.page_rank = pow(2, 63) - 1
            dto.page_rank_weight = 0.0
            self.org_dao.create_update(dto)

    def _small_org_to_org_model(self, small_org):
        return Organization(page_rank=small_org.page_rank, page_rank_info=small_org.page_rank_info,
                            page_rank_weight=small_org.page_rank_weight)