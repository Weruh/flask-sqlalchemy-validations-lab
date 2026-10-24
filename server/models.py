from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('name')
    def validate_name(self, key, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Author name is required')

        name = name.strip()
        # Check saved and unflushed authors before the database constraint runs.
        with db.session.no_autoflush:
            existing = db.session.query(Author).filter_by(name=name).first()
        if existing is not None and existing is not self:
            raise ValueError('Author name must be unique')
        if any(author is not self and isinstance(author, Author) and author.name == name
               for author in (*db.session.new, *db.session.dirty)):
            raise ValueError('Author name must be unique')
        return name

    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        if (not isinstance(phone_number, str) or len(phone_number) != 10
                or not phone_number.isascii() or not phone_number.isdecimal()):
            raise ValueError('Phone number must contain exactly ten digits')
        return phone_number

    def __repr__(self):
        return f'Author(id={self.id}, name={self.name})'

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    category = db.Column(db.String)
    summary = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('title')
    def validate_title(self, key, title):
        if (not isinstance(title, str) or not title.strip()
                or not any(phrase in title.casefold()
                           for phrase in ("won't believe", 'secret', 'top', 'guess'))):
            raise ValueError('Title must contain a clickbait phrase')
        return title

    @validates('content')
    def validate_content(self, key, content):
        if not isinstance(content, str) or len(content) < 250:
            raise ValueError('Content must be at least 250 characters long')
        return content

    @validates('summary')
    def validate_summary(self, key, summary):
        if summary is not None and (not isinstance(summary, str) or len(summary) > 250):
            raise ValueError('Summary must be at most 250 characters long')
        return summary

    @validates('category')
    def validate_category(self, key, category):
        if category not in ('Fiction', 'Non-Fiction'):
            raise ValueError('Category must be Fiction or Non-Fiction')
        return category


    def __repr__(self):
        return f'Post(id={self.id}, title={self.title} content={self.content}, summary={self.summary})'
