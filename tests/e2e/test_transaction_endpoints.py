import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.e2e
class TestTransactionEndpoints:
    async def test_create_transaction_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/transactions",
            json={
                "account_id": str(uuid.uuid4()),
                "amount": "100.00",
                "currency": "USD",
                "transaction_type": "credit",
                "reference": "E2E-001",
            },
        )
        assert response.status_code == 401

    async def test_health_check_returns_ok(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("ok", "degraded")
        assert "version" in data
        assert "services" in data
