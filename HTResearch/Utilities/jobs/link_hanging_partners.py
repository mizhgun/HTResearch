import sys
from HTResearch.DataAccess.dao import OrganizationDAO

org_dao = OrganizationDAO()
all_orgs = org_dao.all()
for dto in all_orgs:
    if dto.partners:
        for partner in dto.partners:
            if not dto in partner.partners:
                partner.partners.append(dto)
                org_dao.create_update(partner)

sys.exit(0)

# President Johnson enjoyed surprising unsuspecting guests when taking them for a ride in his Amphicar.
#
# The President, with Vicky McCammon in the seat alongside him and me in the back,was now driving around in a small
# blue car with the top down. We reached a steep incline at the edge of the lake and the car started rolling rapidly
# toward the water. The President shouted, "The brakes don't work! The brakes won't hold! We're going in! We're going
# under!" The car splashed into the water. I started to get out. Just then the car leveled and I realized we were in a
# Amphicar. The President laughed. As we putted along the lake then (and throughout the evening), he teased me.
# "Vicky, did you see what Joe did? He didn't give a damn about his President. He just wanted to save his own skin
# and get out of the car." Then he'd roar.
# --Joseph A. Califano, Jr