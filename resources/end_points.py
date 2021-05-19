from .holder import RecoveryHolder
from .note_api import NotesApi, NoteApi
from .auth import SignupApi, LoginApi
from .reset_password import ForgotPassword, ResetPasswordConfirm

holder = RecoveryHolder()


def initialize_routes(api):
    api.add_resource(NotesApi, '/api/notes')  # GET ,POST
    api.add_resource(NoteApi, '/api/notes/<id>')  # PUT ,DELETE

    api.add_resource(SignupApi, '/api/auth/signup')
    api.add_resource(LoginApi, '/api/auth/login')

    api.add_resource(ForgotPassword, '/api/auth/forgot')
    api.add_resource(ResetPasswordConfirm, '/api/auth/reset/' + holder.reset_token)  # GET
