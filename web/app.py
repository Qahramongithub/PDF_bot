import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
import itsdangerous
from starlette_admin.contrib.sqla import Admin, ModelView

from db.moduls import engine, User
from web.login import UsernameAndPasswordProvider

app = Starlette()

admin = Admin(engine, title="Example: SQLAlchemy",
              base_url='/',
              auth_provider=UsernameAndPasswordProvider(),
              middlewares=[Middleware(SessionMiddleware, secret_key="qewrerthytju4")],
              )


admin.add_view(ModelView(User,icon='fas fa-users'))

admin.mount_to(app)
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)