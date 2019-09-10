from sqlalchemy import BigInteger, Column, String,Integer
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

class ArticlesForm(Form):

    title = StringField('title')
    content = StringField('content')
    image = StringField('image')
    category = StringField('category')


class Article(DeclarativeBase):
    __tablename__ = 'articles'

    id = Column(Integer,primary_key=True)
    title = Column(String(255), unique=True)
    content = Column(String(255), unique=True)
    image = Column(String(255), unique=True)
    category = Column(String(255), unique=True)
    author = Column(String(255), unique=True)

class User(DeclarativeBase):
    
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255), unique=True)
    email = Column(String(255), unique=True)

class RegisterHandler(SessionMixin, RequestHandler):
    def get(self):
        demoLogin=self.get_cookie("username")
        form = RegisterForm()
        loader = tornado.template.Loader("templates")
        self.write(loader.load("register.html").generate(form=form,demoLogin=demoLogin))
    
    def post(self):
        form = RegisterForm(self.request.arguments)
        user = User(username = form.username.data,password = form.password.data,email =form.email.data)
            
        with self.make_session() as session:
           session.add(user)
           session.commit()
           self.redirect("/")

class LoginHandler(SessionMixin, RequestHandler):
    def get(self):
        demoLogin=self.get_cookie("username")
        form = LoginForm()
        loader = tornado.template.Loader("templates")
        self.write(loader.load("login.html").generate(form=form,demoLogin=demoLogin))
    
    def post(self):
        
        form = LoginForm(self.request.arguments)
            
        username = form.username.data
        password = form.password.data

        with self.make_session() as session:
            
            result = session.query(User).filter_by(username=username).first()

            if result !=0:
                
                
                if result.password==password:
                    key = Fernet.generate_key()
                    #f = Fernet(key)
                    f2 = Fernet(key)
                    #token = f.encrypt(b"{{ username}}")
                    token2 = f2.encrypt(b"{{password}}")
                   

                    if not self.get_cookie("username"):
                        self.set_cookie("username", username)
                        self.set_cookie("password", token2)
                        
            self.redirect("/") 


class MainHandler(SessionMixin,RequestHandler):
    def get(self):
        demoLogin=self.get_cookie("username")
        self.render("templates/mainpage.html",demoLogin=demoLogin)

class ContentHandler(RequestHandler):
    def get(self,name="html"):
        demoLogin=self.get_cookie("username")
        self.render("templates/content.html",demoLogin=demoLogin)
        
class AboutHandler(RequestHandler):
    def get(self):
        demoLogin=self.get_cookie("username")
        self.render("templates/about.html",demoLogin=demoLogin)

class LogoutHandler(RequestHandler):
    def get(self):
        self.clear_cookie("username")
        self.clear_cookie("password")
        self.redirect("/")

class BoardHandler(RequestHandler):
    def get(self):
        demoLogin=self.get_cookie("username")
        self.render("templates/dashboard.html",demoLogin=demoLogin)

class RecordArticleHandler(RequestHandler,SessionMixin):
    def get(self):
        demoLogin=self.get_cookie("username")

        with self.make_session() as session:
            allArticle = session.query(Article).order_by(Article.id.desc()).all()

            self.render("templates/registeredarticles.html",demoLogin=demoLogin,allArticle=allArticle)


class DeleteArticleHandler(RequestHandler,SessionMixin):
    def get(self):
        id = self.get_argument('id', None)

        with self.make_session() as session:
            dell = session.query(Article).filter_by(id = id).first()
            session.delete(dell)
            session.commit()

        self.redirect("/registered")

class UpdateArticleHandler(RequestHandler,SessionMixin):
    id=""
    def get(self):
        global id
        id = self.get_argument('id', None)
        print(id)
        demoLogin=self.get_cookie("username")
        form = ArticlesForm()
        loader = tornado.template.Loader("templates")
        self.write(loader.load("update.html").generate(form=form,demoLogin=demoLogin))

    def post(self):
        form = ArticlesForm(self.request.arguments)
        print(id)
        with self.make_session() as session:
            
            article = session.query(Article).filter_by(id = id).first()

            print(article)

            self.redirect("/registered")
            if form.title.data !="":
                article.title=form.title.data
            if form.content.data !="":
                article.content = form.content.data
            if form.image.data !="":
                article.image = form.image.data
            if form.category.data !="":
                article.category = form.category.data
                     
            session.commit()


        

class  AddArticlesHandler(SessionMixin,RequestHandler):
        def get(self):
            demoLogin=self.get_cookie("username")
            form = ArticlesForm()
            loader = tornado.template.Loader("templates")
            self.write(loader.load("addarticles.html").generate(form=form,demoLogin=demoLogin))
        
        def post(self):
            form = ArticlesForm(self.request.arguments)

            title = form.title.data
            content = form.content.data
            image = form.image.data
            category = form.image.data
            author=self.get_cookie("username")

            article = Article(title=title,content=content,image=image,category=category,author=author)

            with self.make_session() as session:

                session.add(article)
                session.commit()
            
            self.redirect("/")
            
def make_app():


    session_factory = make_session_factory("postgresql://postgres:123456789@127.0.0.1/blog")

    return tornado.web.Application([
        (r"/",MainHandler),
        (r"/style/(.*)",tornado.web.StaticFileHandler, {"path": "./static/style"},),
        (r"/javascript/(.*)",tornado.web.StaticFileHandler, {"path": "./static/javascript"},),
        (r"/about",AboutHandler),
        (r"/register",RegisterHandler),
        (r"/login",LoginHandler),
        (r"/logout",LogoutHandler),
        (r"/dashboard",BoardHandler),
        (r"/addarticles",AddArticlesHandler),
        (r"/registered",RecordArticleHandler),
        (r"/delete",DeleteArticleHandler),
        (r"/update",UpdateArticleHandler),
        (r"/(.*)",ContentHandler),
    ],debug=True,session_factory=session_factory)

    

if __name__=="__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
