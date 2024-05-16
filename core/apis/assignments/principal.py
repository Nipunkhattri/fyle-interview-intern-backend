from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from .schema import TeacherSchema,AssignmentSchema,AssignmentGradeSchema
from core.models.teachers import Teacher
from core.models.assignments import Assignment

principal_power = Blueprint('principal_power',__name__)

@principal_power.route('/teachers',methods=['GET'])
@decorators.authenticate_principal
def teacher_details(p):
    """Get all teachers details"""
    teacher_data = Assignment.getallteachers(_id=p.principal_id)
    teacher_data_dump = TeacherSchema(many=True).dump(teacher_data)
    return APIResponse.respond(data=teacher_data_dump)

@principal_power.route('/assignments',methods=['GET'])
@decorators.authenticate_principal
def get_assignments(p):
    """Get all assignment submited and graded"""
    assignment_data = Assignment.get_assignments_graded_submited(_id=p.principal_id)
    assignment_data_dump = AssignmentSchema(many=True).dump(assignment_data)
    return APIResponse.respond(data=assignment_data_dump)

@principal_power.route('/assignments/grade',methods=['POST'],strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def regrade_assignment(p,incoming_payload):
    """Re-Grade the assignment by principal"""

    update_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    
    update_assignment = Assignment.update_grade(
        principal_id = p.principal_id,
        _id=update_assignment_payload.id,
        grade = update_assignment_payload.grade,
        auth_principal=p
    )

    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(update_assignment)
    return APIResponse.respond(data=graded_assignment_dump)
