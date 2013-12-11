from springpython.context import ApplicationContext
from datetime import datetime

from HTResearch.Utilities.context import DAOContext


def user_info(request):
    info = {'username': ''}

    if 'name' in request.session:
        request.session['last_modified'] = datetime.utcnow()
        info['username'] = request.session['name']

    elif 'user_id' in request.session:
        request.session['last_modified'] = datetime.utcnow()
        uid = request.session['user_id']
        ctx = ApplicationContext(DAOContext())
        dao = ctx.get_object('UserDAO')
        user_dto = dao.find(id=uid)
        info['username'] = user_dto.first_name

    return info