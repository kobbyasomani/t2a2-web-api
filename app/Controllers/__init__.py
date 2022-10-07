from app.controllers.index_controller import index
from app.controllers.users_controller import users
from app.controllers.auth_controller import auth
from app.controllers.questions_controller import questions
from app.controllers.answers_controller import answers
from app.controllers.categories_controller import categories

registerable_controllers = [
    index,
    users,
    auth,
    questions,
    answers,
    categories
]