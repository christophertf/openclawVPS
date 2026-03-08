from app.cpra.deadline_math import compute_deadlines


def test_cpra_deadline_math_examples():
    case = {
        "request_received_datetime": "2026-03-01T10:00:00-08:00",
        "agency_responses": [
            {
                "response_datetime": "2026-03-05T11:00:00-08:00",
                "response_type": "extension",
            },
            {
                "response_datetime": "2026-03-10T12:00:00-08:00",
                "response_type": "determination",
            },
        ],
    }
    out = compute_deadlines(case)
    assert out["extension_claimed"] is True
    assert out["determination_on_time"] is True
