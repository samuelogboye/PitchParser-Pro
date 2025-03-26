from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from pitch.services.parser_service import ParserService
from pitch.celery.tasks import process_pitchdeck

parser_bp = Blueprint("parser", __name__)

@parser_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    return ParserService.upload_file(request.files['file'])

@parser_bp.route('/pitch-decks/<int:pitch_deck_id>', methods=['GET'])
@jwt_required()
def get_pitch_deck(pitch_deck_id):
    return ParserService.get_pitch_deck(pitch_deck_id)

@parser_bp.route('/pitch-decks/<int:pitch_deck_id>/slides', methods=['GET'])
@jwt_required()
def get_slides(pitch_deck_id):
    return ParserService.get_slides(pitch_deck_id)

# get all pick decks
@parser_bp.route('/pitch-decks', methods=['GET'])
@jwt_required()
def get_pitch_decks():
    return ParserService.get_pitch_decks()

@parser_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = process_pitchdeck.AsyncResult(task_id)
    return {
        'status': task.status,
        'result': task.result if task.status == 'SUCCESS' else None,
        'error': str(task.info) if task.status == 'FAILURE' else None
    }