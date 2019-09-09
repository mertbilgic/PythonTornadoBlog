from sqlalchemy import BigInteger, Column, String
import tornado.ioloop
import tornado.web
import tornado.template
from tornado.web import Application, RequestHandler
from tornado.options import define, options, parse_command_line
from tornado_sqlalchemy import (SessionMixin, as_future, declarative_base,make_session_factory)
from wtforms import validators
from wtforms.fields import IntegerField,StringField,PasswordField
from wtforms.validators import Required
from wtforms_tornado import Form
from cryptography.fernet import Fernet

DENEME =""

#Bilgilendirici sınıf tanımları için bir temel sınıf oluşturduk
DeclarativeBase = declarative_base()

define("database-url", type=str, help="postgresql://postgres:123456789@127.0.0.1/blog")
class RegisterForm(Form):

    username = StringField('username')
    password = PasswordField('password')
    email = StringField('email')

class LoginForm(Form):

    username = StringField('username')
    password = PasswordField("password")

class User(DeclarativeBase):
    
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255), unique=True)
    email = Column(String(255), unique=True)

class RegisterHandler(SessionMixin, RequestHandler):
    def get(self):
        form = RegisterForm()
        loader = tornado.template.Loader("templates")
        self.write(loader.load("register.html").generate(form=form,DENEME=DENEME))
    
    def post(self):
        form = RegisterForm(self.request.arguments)
        user = User(username = form.username.data,password = form.password.data,email =form.email.data)
            
        with self.make_session() as session:
           session.add(user)
           session.commit()
           self.render("templates/mainpage.html",DENEME=DENEME)

class LoginHandler(SessionMixin, RequestHandler):
    def get(self):
        form = LoginForm()
        loader = tornado.template.Loader("templates")
        self.write(loader.load("login.html").generate(form=form,DENEME=DENEME))
    
    def post(self):
        
        form = LoginForm(self.request.arguments)
            
        username = form.username.data
        password = form.password.data

        with self.make_session() as session:
            
            result = session.query(User).filter_by(username=username).first()

            if result !=0:
                
                
                if result.password==password:
                    key = Fernet.generate_key()
                    f = Fernet(key)
                    f2 = Fernet(key)
                    token = f.encrypt(b"{{ username}}")
                    token2 = f2.encrypt(b"{{password}}")
                   

                    if not self.get_cookie("username"):
                        self.set_cookie("username", token)
                        self.set_cookie("password", token2)
                        
            self.redirect("/") 


class MainHandler(SessionMixin,RequestHandler):
    def get(self):
        global DENEME
        DENEME=self.get_cookie("username")
        print(DENEME)
        self.render("templates/mainpage.html",DENEME=DENEME)

class ContentHandler(RequestHandler):
    def get(self,name="html"):

        self.render("templates/content.html",DENEME=DENEME)
        
class AboutHandler(RequestHandler):
    def get(self):
        self.render("templates/about.html",DENEME=DENEME)

class LogoutHandler(RequestHandler):
    def get(self):
        #self.clear_cookie("username")
        #self.clear_cookie("password")
        self.redirect("/") 



def make_app():


    session_factory = make_session_factory("postgresql://postgres:123456789@127.0.0.1/blog")

    return tornado.web.Application([
        (r"/",MainHandler),
        (r"/style/(.*)",tornado.web.StaticFileHandler, {"path": "./static/style"},),
        (r"/about",AboutHandler),
        (r"/register",RegisterHandler),
        (r"/login",LoginHandler),
        (r"/logout",LogoutHandler),
        (r"/(.*)",ContentHandler),
    ],debug=True,session_factory=session_factory)

    

if __name__=="__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
