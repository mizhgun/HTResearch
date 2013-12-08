from springpython.context import ApplicationContext
from datetime import datetime

from HTResearch.Utilities.context import DAOContext


def user_info(request):
    info = {'username': ''}

    if 'user_id' in request.session:
        id = request.session['user_id']
        request.session['last_modified'] = datetime.utcnow()
        ctx = ApplicationContext(DAOContext())
        dao = ctx.get_object('UserDAO')
        user_dto = dao.find(id=id)
        info['username'] = user_dto.first_name

    return info