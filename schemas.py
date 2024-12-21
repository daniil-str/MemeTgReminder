from sqlalchemy import db


class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ...