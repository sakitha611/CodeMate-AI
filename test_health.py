from backend.app import create_app

def test_health():
    app=create_app()
    app.config.update(TESTING=True)
    client=app.test_client()
    response=client.get('/health')
    assert response.status_code==200
    assert response.json['status']=='ok'
