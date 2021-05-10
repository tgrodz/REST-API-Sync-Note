from flask import Response, request
from database.models import Note, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError
from resources.errors import SchemaValidationError, NoteAlreadyExistsError, InternalServerError, \
UpdatingNoteError, DeletingNoteError, NoteNotExistsError


class NotesApi(Resource):

    def get(self):
        query = Note.objects()
        notes = Note.objects().to_json()
        return Response(notes, mimetype="application/json", status=200)

    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()
            body = request.get_json()
            user = User.objects.get(id=user_id)
            note = Note(**body, added_by=user)
            note.save()
            user.update(push__notes=note)
            user.save()
            id = note.id
            return {'id': str(id)}, 200
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise NoteAlreadyExistsError
        except Exception as e:
            raise InternalServerError


class NoteApi(Resource):

    @jwt_required()
    def put(self, id):
        try:
            user_id = get_jwt_identity()
            note = Note.objects.get(id=id, added_by=user_id)
            body = request.get_json()
            Note.objects.get(id=id).update(**body)
            return '', 200
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise UpdatingNoteError
        except Exception:
            raise InternalServerError
       
    @jwt_required()
    def delete(self, id):
        try:
            user_id = get_jwt_identity()
            note = Note.objects.get(id=id, added_by=user_id)
            item_id = id   
            note.delete()
            return 'Item by id '+ item_id + ' was successfully deleted', 200 
        except DoesNotExist:
            raise DeletingNoteError
        except Exception:
            raise InternalServerError

    def get(self, id):
        try:
            notes = Note.objects.get(id=id).to_json()
            return Response(notes, mimetype="application/json", status=200)
        except DoesNotExist:
            raise NoteNotExistsError
        except Exception:
            raise InternalServerError
