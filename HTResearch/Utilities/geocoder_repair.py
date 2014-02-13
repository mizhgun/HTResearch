from springpython.context import ApplicationContext
from HTResearch.Utilities.context import DAOContext
from HTResearch.Utilities.geocoder import geocode

# Helper script to fix broken database by adding latlongs
if __name__ == '__main__':
    ctx = ApplicationContext(DAOContext())
    dao = ctx.get_object('OrganizationDAO')
    empty_latlngs = dao.findmany(latlng=[])
    null_latlngs = dao.findmany(latlng__exists=False)
    for dto in empty_latlngs:
        if not dto.address:
            continue
        dto.latlng = geocode(dto.address)
        dao.create_update(dto)
    for dto in null_latlngs:
        if not dto.address:
            continue
        dto.latlng = geocode(dto.address)
        dao.create_update(dto)
