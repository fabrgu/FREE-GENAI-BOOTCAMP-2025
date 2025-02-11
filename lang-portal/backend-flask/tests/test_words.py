def test_get_words(client):
    response = client.get('/api/words')
    assert response.status_code == 200
    data = response.get_json()
    assert 'words' in data
    assert len(data['words']) == 50  # From our test data
    assert data['words'][0]['portuguese'] in ['abrir']
    assert 'total_pages' in data
    assert 'current_page' in data
    assert 'total_words' in data

def test_get_word(client):
    response = client.get('/api/words/1')
    assert response.status_code == 200
    data = response.get_json()

    assert data['word']['portuguese'] == 'ser'
    assert data['word']['english'] == 'to be'

def test_get_word_not_found(client):
    response = client.get('/api/words/999')
    assert response.status_code == 404
