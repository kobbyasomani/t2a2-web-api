from app.controllers.users_controller import users
from app.controllers.auth_controller import auth
from app.controllers.questions_controller import questions

registerable_controllers = [
    users,
    auth,
    questions
]