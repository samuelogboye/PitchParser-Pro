from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pitch.services.parser_service import ParserService
from pitch.utils.logger import log_success
# from pitch.celery.tasks.pitchdeck import process_pitchdeck

parser_bp = Blueprint("parser", __name__)

@parser_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    current_user_id = get_jwt_identity()
    log_success("current_user", current_user_id)
    return ParserService.upload_file(request.files['file'], current_user_id)

@parser_bp.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    return ParserService.get_progress(task_id)

@parser_bp.route('/pitch-decks/<uuid:pitch_deck_id>', methods=['GET'])
@jwt_required()
def get_pitch_deck(pitch_deck_id):
    return ParserService.get_pitch_deck(pitch_deck_id)

@parser_bp.route('/pitch-decks/<uuid:pitch_deck_id>/slides', methods=['GET'])
@jwt_required()
def get_slides(pitch_deck_id):
    return ParserService.get_slides(pitch_deck_id)

# get all pick decks
@parser_bp.route('/pitch-decks', methods=['GET'])
@jwt_required()
def get_pitch_decks():
    return ParserService.get_pitch_decks()

# @parser_bp.route('/tasks/<task_id>', methods=['GET'])
# def get_task_status(task_id):
#     task = process_pitchdeck.AsyncResult(task_id)
#     return {
#         'status': task.status,
#         'result': task.result if task.status == 'SUCCESS' else None,
#         'error': str(task.info) if task.status == 'FAILURE' else None
#     }