from .. import db, login_manager
from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, url_for
import logging

logger = logging.getLogger(__name__)


class Permission:
    READ = 1
    WRITE = 2
    MODERATE = 4
    ADMIN = 8


class Role(db.Document):
    """Users's Roles"""

    name = db.StringField(max_length=64, unique=True)
    default = db.BooleanField(default=False)
    permissions = db.IntField()

    meta = {
        'indexes': [
            'default',
        ]
    }

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'No access': [Permission.READ, Permission.WRITE],
            'Moderator': [Permission.READ, Permission.WRITE,
                          Permission.MODERATE],
            'Administrator': [Permission.READ, Permission.WRITE,
                              Permission.MODERATE, Permission.ADMIN],
        }
        default_role = 'No access'
        for r in roles:
            role = Role.objects(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            role.save()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __str__(self):
        return '%s' % self.name


class User(UserMixin, db.Document):
    """Users with different access roles"""

    email = db.EmailField(max_length=120, unique=True)
    username = db.StringField(max_length=64)
    role = db.ReferenceField(Role)   #####
    password_hash = db.StringField(max_length=128)
    confirmed = db.BooleanField(default=False)
    location = db.StringField(max_length=64)
    member_since = db.DateTimeField(default=datetime.utcnow)
    avatar_hash = db.StringField(max_length=32)

    meta = {
        'allow_inheritance': True,
        'indexes': [
            'email',
        ]
    }

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['APP_ADMIN']:
                self.role = Role.objects(name='Administrator').first()
            if self.role is None:
                self.role = Role.objects(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': str(self.id)}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != str(self.id):
            return False
        self.confirmed = True
        self.save()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': str(self.id)}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.objects(id=data.get('reset')).first()
        if user is None:
            return False
        user.password = new_password
        user.save()
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': str(self.id), 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != str(self.id):
            return False

        self.email = data.get('new_email')
        self.avatar_hash = self.gravatar_hash()
        self.save()
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def to_json(self):
        json_user = {
            'id': str(self.id),
            'email': self.email,
            'member_since': self.member_since,
        }
        return json_user

    def generate_auth_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': str(self.id)}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.objects(id=data['id']).first()

    def __repr__(self):
        return '<User %r>' % self.email

    def __str__(self):
        return 'username=%s' % self.email


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """User loader func is needed by flask-login to load users
       which DB engine dependent"""
    return User.objects(id=user_id).first()


def update_roles():
    """create or update user roles"""
    Role.insert_roles()


