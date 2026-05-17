from app.services.health_service import HealthService


class TestHealthService:
    def test_returns_expected_shape(self):
        result = HealthService.get_health_status()
        assert result["status"] == "healthy"
        assert result["service"] == "FastAPI App"
        assert "timestamp" in result


class TestHealthRoute:
    def test_health_endpoint(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "healthy"
