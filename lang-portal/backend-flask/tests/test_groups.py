def test_get_groups(client):
    response = client.get('/api/groups')
    assert response.status_code == 200
    data = response.get_json()
    assert 'groups' in data
    assert len(data['groups']) == 2
    assert data['groups'][0]['group_name'] == 'Core Adjectives'
    assert data['groups'][0]['word_count'] == 60

def test_get_group(client):
    response = client.get('/api/groups/1')
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['group_name'] == 'Core Verbs'
    assert data['word_count'] == 40

def test_get_group_words(client):
    response = client.get('/api/groups/1/words')
    if response.status_code == 500:
        print("Error:", response.get_json().get('error'))
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'words' in data
    assert len(data['words']) == 10
    assert data['words'][0]['portuguese'] in ['abrir', 'acabar']

def test_get_group_words_raw(client):
    response = client.get('/api/groups/1/words/raw')
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'items' in data
    assert len(data['items']) == 40