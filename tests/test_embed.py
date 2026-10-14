import pytest
@pytest.mark.asyncio
async def test_search(client):
    await client.post("/api/docs", json={"title": "VPN", "text": "Corporate VPN is required for staging access and MFA."})
    r = await client.get("/api/search", params={"q": "VPN staging"})
    assert r.status_code == 200
    assert r.json()["hits"]
