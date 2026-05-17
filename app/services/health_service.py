from datetime import datetime


class HealthService:
    @staticmethod
    def get_health_status():
        """Get current health status"""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "FastAPI App"
        }

