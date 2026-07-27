import uuid
from app.extensions import db

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)

    users = db.relationship('User', back_populates='role')

    def __repr__(self):
        return f'<Role {self.name}>'