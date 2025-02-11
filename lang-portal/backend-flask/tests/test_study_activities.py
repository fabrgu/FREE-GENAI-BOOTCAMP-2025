def test_get_study_activities(client):
    response = client.get('/api/study_activities')
    assert response.status_code == 200
    data = response.get_json()
    
    assert len(data) == 1  # From our test data
    assert data[0]['title'] == 'Typing Tutor'

def test_get_study_activity(client):
    response = client.get('/api/study_activities/1')
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['title'] == 'Typing Tutor'

def test_get_study_activity_not_found(client):
    response = client.get('/api/study_activities/999')
    assert response.status_code == 404 