from core.models.assignments import AssignmentStateEnum, GradeEnum


def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400

def test_grade_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )
    # assert response.status_code == 400

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_regrade_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    # assert response.status_code == 400

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B


def test_regrade_assignment_fail_unauthorized(client, h_principal):
    # Use a non-principal user token
    response = client.post(
        '/principal/assignments/grade',
        headers= {"user_id":5, "principal_id":2},
        json={
            'id':4,
            'grade':GradeEnum.B.value
        }
    )

    assert response.status_code == 401

def test_get_assignment_fail_unauthorized(client, h_principal):
    # Use a non-principal user token
    response = client.get(
        '/principal/assignments',
        headers= {"user_id":5, "principal_id":2},
    )

    assert response.status_code == 401


def test_get_teachers_fail_unauthorized(client, h_principal):
    # Use a non-principal user token
    response = client.get(
        '/principal/teachers',
        headers= {"user_id":5, "principal_id":2},
    )

    assert response.status_code == 401


def test_get_teachers(client, h_principal):
    response = client.get(
        '/principal/teachers',
        headers=h_principal
    )

    assert response.status_code == 200

    # data = response.json['data']
    # for assignment in data:
    #     assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]
