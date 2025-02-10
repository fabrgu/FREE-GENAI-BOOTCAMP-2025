from flask import request, jsonify, g
from flask_cors import cross_origin
from datetime import datetime
import math

def load(app):
  @app.route('/api/study_sessions', methods=['GET'])
  @cross_origin()
  def get_study_sessions():
    try:
      cursor = app.db.cursor()
      
      # Get pagination parameters
      page = request.args.get('page', 1, type=int)
      per_page = request.args.get('per_page', 10, type=int)
      offset = (page - 1) * per_page

      # Get total count
      cursor.execute('''
        SELECT COUNT(*) as count 
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
      ''')
      total_count = cursor.fetchone()['count']

      # Get paginated sessions
      cursor.execute('''
        SELECT 
          ss.id,
          ss.group_id,
          g.name as group_name,
          sa.id as activity_id,
          sa.name as activity_name,
          ss.created_at,
          COUNT(wri.id) as review_items_count
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
        LEFT JOIN word_review_items wri ON wri.study_session_id = ss.id
        GROUP BY ss.id
        ORDER BY ss.created_at DESC
        LIMIT ? OFFSET ?
      ''', (per_page, offset))
      sessions = cursor.fetchall()

      return jsonify({
        'items': [{
          'id': session['id'],
          'group_id': session['group_id'],
          'group_name': session['group_name'],
          'activity_id': session['activity_id'],
          'activity_name': session['activity_name'],
          'start_time': session['created_at'],
          'end_time': session['created_at'],  # For now, just use the same time since we don't track end time
          'review_items_count': session['review_items_count']
        } for session in sessions],
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(total_count / per_page)
      })
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  @app.route('/api/study_sessions/<id>', methods=['GET'])
  @cross_origin()
  def get_study_session(id):
    try:
      cursor = app.db.cursor()
      
      # Get session details
      cursor.execute('''
        SELECT 
          ss.id,
          ss.group_id,
          g.name as group_name,
          sa.id as activity_id,
          sa.name as activity_name,
          ss.created_at,
          COUNT(wri.id) as review_items_count
        FROM study_sessions ss
        JOIN groups g ON g.id = ss.group_id
        JOIN study_activities sa ON sa.id = ss.study_activity_id
        LEFT JOIN word_review_items wri ON wri.study_session_id = ss.id
        WHERE ss.id = ?
        GROUP BY ss.id
      ''', (id,))
      
      session = cursor.fetchone()
      if not session:
        return jsonify({"error": "Study session not found"}), 404

      # Get pagination parameters
      page = request.args.get('page', 1, type=int)
      per_page = request.args.get('per_page', 10, type=int)
      offset = (page - 1) * per_page

      # Get the words reviewed in this session with their review status
      cursor.execute('''
        SELECT 
          w.*,
          COALESCE(SUM(CASE WHEN wri.correct = 1 THEN 1 ELSE 0 END), 0) as session_correct_count,
          COALESCE(SUM(CASE WHEN wri.correct = 0 THEN 1 ELSE 0 END), 0) as session_wrong_count
        FROM words w
        JOIN word_review_items wri ON wri.word_id = w.id
        WHERE wri.study_session_id = ?
        GROUP BY w.id
        ORDER BY w.portuguese
        LIMIT ? OFFSET ?
      ''', (id, per_page, offset))
      
      words = cursor.fetchall()

      # Get total count of words
      cursor.execute('''
        SELECT COUNT(DISTINCT w.id) as count
        FROM words w
        JOIN word_review_items wri ON wri.word_id = w.id
        WHERE wri.study_session_id = ?
      ''', (id,))
      
      total_count = cursor.fetchone()['count']

      return jsonify({
        'session': {
          'id': session['id'],
          'group_id': session['group_id'],
          'group_name': session['group_name'],
          'activity_id': session['activity_id'],
          'activity_name': session['activity_name'],
          'start_time': session['created_at'],
          'end_time': session['created_at'],  # For now, just use the same time
          'review_items_count': session['review_items_count']
        },
        'words': [{
          'id': word['id'],
          'portuguese': word['portuguese'],
          'english': word['english'],
          'correct_count': word['session_correct_count'],
          'wrong_count': word['session_wrong_count']
        } for word in words],
        'total': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': math.ceil(total_count / per_page)
      })
    except Exception as e:
      return jsonify({"error": str(e)}), 500


  @app.route('/api/study_sessions/<id>/review', methods=['POST'])
  @cross_origin()
  def create_study_session_review(id):
    try:
      cursor = app.db.cursor()
      data = request.get_json()
      word_id = data.get('word_id')
      correct = data.get('correct')

      # Validate required fields
      error_messages = []
      if not word_id:
        error_messages.append('word_id is required')
      if not correct:
        error_messages.append('correct is required')
      
      if error_messages.length > 0:
        return jsonify({'error': ' '.join(error_messages)}), 400

      # Verify word exists
      cursor.execute('SELECT id FROM words WHERE id = ?', (word_id))
      if not cursor.fetchone():
        return jsonify({'error': 'Word not found'}), 404

      # Verify study session exists
      cursor.execute('SELECT id FROM study_sessions WHERE id = ?', (id))
      if not cursor.fetchone():
        return jsonify({'error': 'Study session not found'}), 404

      # Create word review item
      cursor.execute('''
        INSERT INTO word_review_items (word_id, study_session_id, correct, created_at)
        VALUES (?, ?, ?, datetime('now'))
        RETURNING id, word_id, study_session_id, correct, created_at
      ''', (word_id, id, 1 if correct else 0))

      review = cursor.fetchone()
      app.db.commit()

      # Format response
      response = {
        'id': review['id'],
        'word_id': review['word_id'],
        'study_session_id': review['study_session_id'],
        'correct': bool(review['correct']),
        'created_at': review['created_at']
      }

      return jsonify(response), 201

    except Exception as e:
      app.db.rollback()
      print(f"Error creating word review: {str(e)}")
      return jsonify({'error': 'Internal server error'}), 500

  @app.route('/api/study_sessions/reset', methods=['POST'])
  @cross_origin()
  def reset_study_sessions():
    try:
      cursor = app.db.cursor()
      
      # First delete all word review items since they have foreign key constraints
      cursor.execute('DELETE FROM word_review_items')
      
      # Then delete all study sessions
      cursor.execute('DELETE FROM study_sessions')
      
      app.db.commit()
      
      return jsonify({"message": "Study history cleared successfully"}), 200
    except Exception as e:
      return jsonify({"error": str(e)}), 500

  @app.route('/api/study_sessions', methods=['POST'])
  @cross_origin()
  def create_study_session():
    try:
      cursor = app.db.cursor()
      data = request.get_json()
      group_id = data.get('group_id')
      activity_id = data.get('activity_id')

      # Validate required fields
      error_messages = []
      if not group_id:
        error_messages.append('group_id is required.')
      if not activity_id:
        error_messages.append('activity_id is required.')
      
      if error_messages.length > 0:
        return jsonify({'error': ' '.join(error_messages)}), 400

      # Verify group exists
      cursor.execute('SELECT id FROM groups WHERE id = ?', (group_id,))
      if not cursor.fetchone():
        return jsonify({'error': 'Group not found'}), 404

      # Verify activity exists
      cursor.execute('SELECT id FROM study_activities WHERE id = ?', (activity_id,))
      if not cursor.fetchone():
        return jsonify({'error': 'Study activity not found'}), 404

      # Create new study session
      cursor.execute('''
        INSERT INTO study_sessions (group_id, study_activity_id, created_at)
        VALUES (?, ?, datetime('now'))
        RETURNING id, group_id, study_activity_id, created_at
      ''', (group_id, activity_id))

      session = cursor.fetchone()
      app.db.commit()

      # Format response
      response = {
        'id': session['id'],
        'group_id': session['group_id'],
        'study_activity_id': session['study_activity_id'],
        'created_at': session['created_at']
      }

      return jsonify(response), 201

    except Exception as e:
      app.db.rollback()
      print(f"Error creating study session: {str(e)}")
      return jsonify({'error': 'Internal server error'}), 500

