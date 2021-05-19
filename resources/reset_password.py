import json

from flask import request, render_template, Response
from flask_jwt_extended import create_access_token, decode_token
from data.models import User
from flask_restful import Resource
import datetime
from resources.errors import SchemaValidationError, InternalServerError, \
    EmailDoesnotExistsError, BadTokenError, ExpiredTokenError
from jwt.exceptions import ExpiredSignatureError, DecodeError, \
    InvalidTokenError

from resources.holder import RecoveryHolder
from services.mail_service_gmail import send_email

sender_by = 'support@sync-note.com'


class ForgotPassword(Resource):
    def post(self):
        url = request.host_url + 'api/auth/reset/'
        try:
            body = request.get_json()
            email = body.get('email')
            new_password = body.get('new_password')
            if not email or not new_password:
                raise SchemaValidationError

            user = User.objects.get(email=email)
            if not user:
                raise EmailDoesnotExistsError

            holder = RecoveryHolder()
            holder.reset_token = create_access_token(str(user.id), expires_delta=holder.expires)
            holder.password = new_password

            send_email('[Sync-note] Reset Your Password',
                       sender=sender_by,
                       recipients=[user.email],
                       text_body=render_template('email/reset_password.txt', url=url + holder.reset_token),
                       html_body=render_template('email/reset_password.html', url=url + holder.reset_token))

            response_data = {
                "status": "waiting_confirm",
                "info": "Sent email - check your email to confirm new password"
            }
            return Response(json.dumps(response_data), mimetype="application/json", status=200)

        except SchemaValidationError:
            raise SchemaValidationError
        except EmailDoesnotExistsError:
            raise EmailDoesnotExistsError
        except Exception as e:
            print('--Exception ' + str(e))
            raise InternalServerError


# Temporary unique link
class ResetPasswordConfirm(Resource):
    def get(self):
        holder = RecoveryHolder()
        try:

            if not holder.reset_token or not holder.password:
                raise SchemaValidationError

            user_id = decode_token(holder.reset_token)['identity']

            user = User.objects.get(id=user_id)
            user.modify(password=holder.password)
            user.hash_password()
            user.save()

            send_email('[Sync-note] Password reset successful',
                       sender=sender_by,
                       recipients=[user.email],
                       text_body='Password reset was successful',
                       html_body='<p>Password reset was successful</p>')

            return Response(json.dumps(
                {
                    'tmp_token': holder.reset_token,
                    'new_pass': holder.password
                }),
                mimetype="application/json", status=200)

        except ExpiredSignatureError:
            raise ExpiredTokenError
        except (DecodeError, InvalidTokenError):
            raise BadTokenError
        except Exception as e:
            print('--Exception ' + str(e))
            raise InternalServerError
