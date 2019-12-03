from datetime import datetime
# from app import db
from app import db, loginManager, app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@loginManager.user_loader
def loadUser(userId):
    return User.query.get(int(userId))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)    
    image = db.Column(db.String(20), nullable=False, default='default.jpg') 
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def getResetToken(self, expiresSec = 1800):
        s = Serializer(app.config['SECRET_KEY'], expiresSec)
        return s.dumps({ 'userId' : self.id }).decode('utf-8') 

    @staticmethod
    def verifyResetToken(token):
        s = Serializer(app.config['SECRET_KEY'], expiresSec)
        try:
            userId = s.loads(token)['userId']
        except:
            return None
        return User.query.get(userId)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image}')"
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
