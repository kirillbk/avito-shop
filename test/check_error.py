from httpx import Response


def check_error(response: Response, status: int):
    assert response.status_code == status
    data = response.json()
    assert "errors" in data
    assert isinstance(data["errors"], str)
