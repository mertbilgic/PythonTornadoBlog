import tornado.ioloop
import tornado.web



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/mainpage.html")

class ContentHandler(tornado.web.RequestHandler):
    def get(self,name="html"):

        self.render("templates/content.html")
        

class AboutHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/about.html")



def make_app():
    return tornado.web.Application([
        (r"/",MainHandler),
        (r"/style/(.*)",tornado.web.StaticFileHandler, {"path": "./templates/style"},),
        (r"/about",AboutHandler),
        (r"/(.*)",ContentHandler),
    ],debug=True)

    

if __name__=="__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
