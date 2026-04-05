from fastapi.testclient import TestClient


def bootstrap_admin(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/auth/bootstrap-admin",
        json={
            "email": "admin@example.com",
            "full_name": "Admin User",
            "password": "StrongPass123",
        },
    )
    assert response.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "StrongPass123"},
    )
    assert login.status_code == 200
    return login.json()


def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def test_admin_can_create_user_and_record(client: TestClient) -> None:
    token_pair = bootstrap_admin(client)

    create_user = client.post(
        "/api/v1/users",
        json={
            "email": "analyst@example.com",
            "full_name": "Analyst User",
            "password": "AnalystPass123",
            "role": "analyst",
        },
        headers=auth_headers(token_pair["access_token"]),
    )
    assert create_user.status_code == 201

    create_record = client.post(
        "/api/v1/records",
        json={
            "amount": 3200.50,
            "entry_type": "income",
            "category": "salary",
            "entry_date": "2026-04-01",
            "notes": "April salary",
        },
        headers=auth_headers(token_pair["access_token"]),
    )
    assert create_record.status_code == 201
    assert create_record.json()["category"] == "salary"


def test_viewer_cannot_list_records(client: TestClient) -> None:
    token_pair = bootstrap_admin(client)

    create_user = client.post(
        "/api/v1/users",
        json={
            "email": "viewer@example.com",
            "full_name": "Viewer User",
            "password": "ViewerPass123",
            "role": "viewer",
        },
        headers=auth_headers(token_pair["access_token"]),
    )
    assert create_user.status_code == 201

    viewer_login = client.post(
        "/api/v1/auth/login",
        json={"email": "viewer@example.com", "password": "ViewerPass123"},
    )
    assert viewer_login.status_code == 200

    list_records = client.get(
        "/api/v1/records",
        headers=auth_headers(viewer_login.json()["access_token"]),
    )
    assert list_records.status_code == 403


def test_analyst_can_view_records_but_not_create(client: TestClient) -> None:
    token_pair = bootstrap_admin(client)

    create_analyst = client.post(
        "/api/v1/users",
        json={
            "email": "analyst2@example.com",
            "full_name": "Analyst Two",
            "password": "AnalystPass123",
            "role": "analyst",
        },
        headers=auth_headers(token_pair["access_token"]),
    )
    assert create_analyst.status_code == 201

    admin_create_record = client.post(
        "/api/v1/records",
        json={
            "amount": 410.00,
            "entry_type": "expense",
            "category": "rent",
            "entry_date": "2026-04-02",
            "notes": "Office rent",
        },
        headers=auth_headers(token_pair["access_token"]),
    )
    assert admin_create_record.status_code == 201

    analyst_login = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst2@example.com", "password": "AnalystPass123"},
    )
    assert analyst_login.status_code == 200
    analyst_headers = auth_headers(analyst_login.json()["access_token"])

    list_records = client.get("/api/v1/records", headers=analyst_headers)
    assert list_records.status_code == 200
    assert len(list_records.json()["items"]) == 1

    create_record = client.post(
        "/api/v1/records",
        json={
            "amount": 99,
            "entry_type": "expense",
            "category": "tools",
            "entry_date": "2026-04-03",
        },
        headers=analyst_headers,
    )
    assert create_record.status_code == 403


def test_dashboard_summary_and_soft_delete(client: TestClient) -> None:
    token_pair = bootstrap_admin(client)
    headers = auth_headers(token_pair["access_token"])

    create_income = client.post(
        "/api/v1/records",
        json={
            "amount": 1000,
            "entry_type": "income",
            "category": "salary",
            "entry_date": "2026-04-01",
        },
        headers=headers,
    )
    assert create_income.status_code == 201

    create_expense = client.post(
        "/api/v1/records",
        json={
            "amount": 200,
            "entry_type": "expense",
            "category": "food",
            "entry_date": "2026-04-01",
        },
        headers=headers,
    )
    assert create_expense.status_code == 201

    summary = client.get("/api/v1/dashboard/summary", headers=headers)
    assert summary.status_code == 200
    data = summary.json()
    assert float(data["total_income"]) == 1000.0
    assert float(data["total_expenses"]) == 200.0
    assert float(data["net_balance"]) == 800.0

    delete_record = client.delete(f"/api/v1/records/{create_expense.json()['id']}", headers=headers)
    assert delete_record.status_code == 200

    list_records = client.get("/api/v1/records", headers=headers)
    assert list_records.status_code == 200
    assert len(list_records.json()["items"]) == 1


def test_logout_revokes_access_and_refresh_tokens(client: TestClient) -> None:
    token_pair = bootstrap_admin(client)
    headers = auth_headers(token_pair["access_token"])

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": token_pair["refresh_token"]},
        headers=headers,
    )
    assert logout.status_code == 204

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 401

    refresh = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token_pair["refresh_token"]},
    )
    assert refresh.status_code == 401


def test_records_csv_export_and_report_generation(client: TestClient) -> None:
    token_pair = bootstrap_admin(client)
    headers = auth_headers(token_pair["access_token"])

    client.post(
        "/api/v1/records",
        json={
            "amount": 1500,
            "entry_type": "income",
            "category": "salary",
            "entry_date": "2026-04-01",
            "notes": "Primary salary",
        },
        headers=headers,
    )
    client.post(
        "/api/v1/records",
        json={
            "amount": 320,
            "entry_type": "expense",
            "category": "utilities",
            "entry_date": "2026-04-02",
            "notes": "Electricity bill",
        },
        headers=headers,
    )

    export_records = client.get(
        "/api/v1/records/export/csv?search=salary",
        headers=headers,
    )
    assert export_records.status_code == 200
    assert export_records.headers["content-type"].startswith("text/csv")
    assert "salary" in export_records.text
    assert "entry_type" in export_records.text

    run_report = client.post(
        "/api/v1/reports/run",
        json={"report_name": "manual_eval", "lookback_days": 30},
        headers=headers,
    )
    assert run_report.status_code == 201

    list_reports = client.get("/api/v1/reports?page=1&page_size=5", headers=headers)
    assert list_reports.status_code == 200
    assert list_reports.json()["meta"]["total_items"] >= 1

    report_id = run_report.json()["id"]
    export_report = client.get(f"/api/v1/reports/{report_id}/csv", headers=headers)
    assert export_report.status_code == 200
    assert "report_name" in export_report.text
    assert "net_balance" in export_report.text
