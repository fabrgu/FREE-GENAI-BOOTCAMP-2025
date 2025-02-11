
def test_get_dashboard_stats(client):
    response = client.get('/api/dashboard/recent-session')
    assert response.status_code == 200
    
 