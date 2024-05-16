import enum
from core import db
from core.apis.decorators import AuthPrincipal
from core.libs import helpers, assertions
from core.models.teachers import Teacher
from core.models.students import Student
from core.models.principals import Principal
from sqlalchemy.types import Enum as BaseEnum


class GradeEnum(str, enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'


class AssignmentStateEnum(str, enum.Enum):
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    GRADED = 'GRADED'


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, db.Sequence('assignments_id_seq'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.id), nullable=True)
    content = db.Column(db.Text)
    grade = db.Column(BaseEnum(GradeEnum))  
    state = db.Column(BaseEnum(AssignmentStateEnum), default=AssignmentStateEnum.DRAFT, nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False, onupdate=helpers.get_utc_now)

    def __repr__(self):
        return '<Assignment %r>' % self.id

    @classmethod
    def filter(cls, *criterion):
        db_query = db.session.query(cls)
        return db_query.filter(*criterion)

    @classmethod
    def get_by_id(cls, _id):
        return cls.filter(cls.id == _id).first()

    @classmethod
    def upsert(cls, assignment_new: 'Assignment'):
        if assignment_new.id is not None:
            assignment = Assignment.get_by_id(assignment_new.id)
            assertions.assert_found(assignment, 'No assignment with this id was found')
            assertions.assert_valid(assignment.state == AssignmentStateEnum.DRAFT,
                                    'only assignment in draft state can be edited')
            assertions.assert_valid(assignment.content is not None, 'assignment with empty content cannot be submitted')
            
            assignment.content = assignment_new.content
        else:
            assignment = assignment_new
            assertions.assert_valid(assignment.content is not None, 'assignment with empty content cannot be created ')
            db.session.add(assignment)

        # db.session.flush()
        return assignment

    @classmethod
    def submit(cls, _id, teacher_id, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        assertions.assert_found(assignment, 'No assignment with this id was found')
        assertions.assert_valid(assignment.student_id == auth_principal.student_id, 'This assignment belongs to some other student')
        assertions.assert_valid(assignment.content is not None, 'assignment with empty content cannot be submitted')
        assertions.assert_valid(assignment.state == AssignmentStateEnum.DRAFT,
                                    'only a draft assignment can be submitted')
        
        assignment.state = AssignmentStateEnum.SUBMITTED
        assignment.teacher_id = teacher_id
        db.session.flush()

        return assignment

    @classmethod
    def mark_grade(cls, teacher_id,_id, grade, auth_principal: AuthPrincipal):
        teacher = Teacher.get_by_id(_id=teacher_id)
        assertions.assert_found(teacher, 'No Teacher with this id was found')
        assignment = Assignment.get_by_id(_id)
        assertions.assert_found(assignment, 'No assignment with this id was found')
        assertions.assert_valid(grade is not None, 'assignment with empty grade cannot be graded')
        assertions.assert_valid(assignment.teacher_id == auth_principal.teacher_id, 'This assignment belongs to some other teacher')
        assertions.assert_valid(grade in GradeEnum.__members__, 'Invalid grade value')
        assertions.assert_valid(assignment.state == AssignmentStateEnum.SUBMITTED,
                                    'only a submitted assignment can be graded')
        assignment.grade = grade
        assignment.state = AssignmentStateEnum.GRADED
        db.session.flush()

        return assignment
    
    @classmethod
    def update_grade(cls,principal_id, _id, grade, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        principal = Principal.get_by_id(_id=principal_id)
        assertions.assert_found(principal, 'No Principal with this id was found')
        assertions.assert_found(assignment, 'No assignment with this id was found')
        assertions.assert_valid(grade is not None, 'assignment with empty grade cannot be graded')
        print(assignment.state)
        assertions.assert_valid(
            assignment.state in (AssignmentStateEnum.GRADED, AssignmentStateEnum.SUBMITTED),
            'If an assignment is not in Graded or Submitted state, it cannot be graded by principal'
        )

        assignment.grade = grade
        assignment.state = AssignmentStateEnum.GRADED
        db.session.flush()

        return assignment

    @classmethod
    def get_assignments_by_student(cls, _id):
        student = Student.get_by_id(_id)
        assertions.assert_found(student, 'No Student with this id was found')
        return cls.filter(cls.student_id == _id).all()

    @classmethod
    def get_assignments_by_teacher(cls, _id):
        teacher = Teacher.get_by_id(_id)
        assertions.assert_found(teacher, 'No Teacher with this id was found')
        return cls.query.filter_by(teacher_id=_id).filter(cls.state.in_(['SUBMITTED', 'GRADED'])).all()

    @classmethod
    def get_assignments_graded_submited(cls,_id):
        principal = Principal.get_by_id(_id)
        assertions.assert_found(principal, 'No Principal with this id was found')
        return cls.filter(
            (Assignment.state == AssignmentStateEnum.SUBMITTED) | 
            (Assignment.state == AssignmentStateEnum.GRADED)
        ).all()

    @classmethod
    def getallteachers(cls,_id):
        principal = Principal.get_by_id(_id)
        assertions.assert_found(principal, 'No Principal with this id was found')
        return cls.query.all()