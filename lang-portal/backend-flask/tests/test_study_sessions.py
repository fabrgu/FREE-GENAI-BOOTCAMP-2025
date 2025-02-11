def test_get_study_sessions(client):
    response = client.get('/api/study_sessions')
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'items' in data
    assert 'total' in data
    assert 'page' in data
    assert 'per_page' in data

def test_create_study_session(client):
    response = client.post('/api/study_sessions', json={
        'group_id': 1,
        'activity_id': 1
    })
    
    if response.status_code != 201:
        print("\nError Response:", response.get_json())
    
    assert response.status_code == 201
    data = response.get_json()
    
    assert 'id' in data
    assert data['group_id'] == 1
    assert data['study_activity_id'] == 1

def test_create_study_session_review(client):
    # First create a session
    session_response = client.post('/api/study_sessions', json={
        'group_id': 1,
        'activity_id': 1
    })
    session_id = session_response.get_json()['id']
    
    # Then create a review
    response = client.post(f'/api/study_sessions/{session_id}/review', json={
        'word_id': 1,
        'correct': True
    })
    assert response.status_code == 201
    data = response.get_json()
    
    assert data['word_id'] == 1
    assert data['study_session_id'] == session_id
    assert data['correct'] == True

def test_get_study_session(client):
    # First create a session
    session_response = client.post('/api/study_sessions', json={
        'group_id': 1,
        'activity_id': 1
    })
    session_id = session_response.get_json()['id']
    
    # Get the session
    response = client.get(f'/api/study_sessions/{session_id}')
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'session' in data
    assert data['session']['group_id'] == 1
    assert data['session']['activity_id'] == 1

def test_create_study_session_invalid_group(client):
    response = client.post('/api/study_sessions', json={
        'group_id': 999,
        'activity_id': 1
    })
    print("\nError Response:", response.get_json())
    assert response.status_code == 404

def test_create_study_session_missing_fields(client):
    response = client.post('/api/study_sessions', json={
        'group_id': 1
    })
    assert response.status_code == 400

def test_reset_study_sessions(client):
    # First create a session
    client.post('/api/study_sessions', json={
        'group_id': 1,
        'activity_id': 1
    })
    
    # Reset all sessions
    response = client.post('/api/study_sessions/reset')
    assert response.status_code == 200
    
    # Verify no sessions exist
    get_response = client.get('/api/study_sessions')
    data = get_response.get_json()
    assert data['total'] == 0 