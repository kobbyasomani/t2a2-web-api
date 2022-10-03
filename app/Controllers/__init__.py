from app.controllers.users_controller import users
from app.controllers.auth_controller import auth
from app.controllers.questions_controller import questions
from app.controllers.categories_controller import categories

registerable_controllers = [
    users,
    auth,
    questions,
    categories
]