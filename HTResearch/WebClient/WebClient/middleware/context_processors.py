from springpython.context import ApplicationContext

from HTResearch.Utilities.context import DAOContext


def user_info(request):
    info = {'username': '', 'user_id': ''}

    if hasattr(request, 'session'):
        if 'name' in request.session and 'user_id' in request.session:
            info['username'] = request.session['name']
            info['user_id'] = request.session['user_id']

        elif 'user_id' in request.session:
            uid = request.session['user_id']
            ctx = ApplicationContext(DAOContext())
            dao = ctx.get_object('UserDAO')
            user_dto = dao.find(id=uid)
            info['username'] = user_dto.first_name + ' ' + user_dto.last_name
            info['user_id'] = uid

    return info