import pytest
import sqlite3
import os
from flask import Flask
from routes import dashboard, groups, study_sessions, words, study_activities
from lib.db import init_db, db

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['DATABASE'] = ':memory:'
    app.config['TESTING'] = True
    
    # Set db instance on app
    app.db = db
    
    # Initialize routes
    dashboard.load(app)
    groups.load(app)
    study_sessions.load(app)
    study_activities.load(app)
    words.load(app)
    
    # Initialize DB
    with app.app_context():
        init_db()
        cursor = db.cursor()
        
        # Clear any existing data
        cursor.execute('DELETE FROM word_review_items')
        cursor.execute('DELETE FROM word_groups')
        cursor.execute('DELETE FROM words')
        cursor.execute('DELETE FROM groups')
        cursor.execute('DELETE FROM study_activities')
        cursor.execute('DELETE FROM study_sessions')
        
        # Reset autoincrement counters
        cursor.execute('DELETE FROM sqlite_sequence')
        
        db.commit()
        
        # Import test data from JSON files
        db.import_word_json(
            cursor=cursor,
            group_name='Core Verbs',
            data_json_path='seed/data_verbs.json'
        )
        
        db.import_word_json(
            cursor=cursor,
            group_name='Core Adjectives',
            data_json_path='seed/data_adjectives.json'
        )
        
        db.import_study_activities_json(
            cursor=cursor,
            data_json_path='seed/study_activities.json'
        )
        
    yield app

@pytest.fixture
def client(app):
    return app.test_client() 