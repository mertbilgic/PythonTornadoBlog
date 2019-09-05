from sqlalchemy import BigInteger, Column, String
import tornado.ioloop
import tornado.web
from tornado.web import Application, RequestHandler
from tornado.options import define, options, parse_command_line
from tornado_sqlalchemy import (SessionMixin, as_future, declarative_base,make_session_factory)

#Bilgilendirici sınıf tanımları için bir temel sınıf oluşturduk
DeclarativeBase = declarative_base()


define("database-url", type=str, help="postgresql://postgres:123456789@127.0.0.1/blog")


class User(DeclarativeBase):
    
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255), unique=True)
    email = Column(String(255), unique=True)

class RegisterHandler(SessionMixin, RequestHandler):
    def get(self):
        with self.make_session() as session:
            count = session.query(User).count()
            self.write("{} users so far!".format(count))

class MainHandler(RequestHandler):
    def get(self):
        self.render("templates/mainpage.html")

class ContentHandler(RequestHandler):
    def get(self,name="html"):

        self.render("templates/content.html")
        

class AboutHandler(RequestHandler):
    def get(self):
        self.render("templates/about.html")



def make_app():


    session_factory = make_session_factory("postgresql://postgres:123456789@127.0.0.1/blog")

    return tornado.web.Application([
        (r"/",MainHandler),
        (r"/style/(.*)",tornado.web.StaticFileHandler, {"path": "./templates/style"},),
        (r"/about",AboutHandler),
        (r"/register",RegisterHandler),
        (r"/(.*)",ContentHandler),
    ],debug=True,session_factory=session_factory)

    

if __name__=="__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
