import tornado.ioloop
import tornado.web
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import databaseClient as db 


class TemplateRendering:
    def render_template(self, template_name, variables={}):
        template_dirs = [ 'views' ]
        env = Environment(
            loader = FileSystemLoader(template_dirs),
            auto_reload=True,
            autoescape=False
        )
        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        content = template.render(variables)
        return content

class BaseHandler(tornado.web.RequestHandler,TemplateRendering):
    def get_current_user(self):
        user_cookie = self.get_secure_cookie("user")
        if user_cookie:
           return user_cookie
        return None

class MainHandler(BaseHandler):
    def get(self):
        self.write(self.render_template('firstpage.html'))
        
class Login(BaseHandler):
    def get(self):
        self.write(self.render_template('login.html'))
        
    def post(self):
        username = self.get_argument("user")
        password = self.get_argument("pass")
        #print(username,hash(password))
        #print(hash(password))
        if(db.check_user(username,password)):
            self.set_secure_cookie("user", username, expires_days=5/86400)   
            self.write({'url': "/home"})
        else:
            self.write({'url': '/login'})
        
class Register(BaseHandler):
    def get(self):
        self.write(self.render_template('register.html'))

    def post(self):
        username= self.get_argument('user')
        password= self.get_argument('pass') 
        if(not db.checkUserName(username)):
            print('oluşturuldu')
            db.register_user(username,password)
            self.set_secure_cookie("user", username, expires_days=5/86400)   
            self.write({'url': "/home"})
        else:
            self.write({'message':'user already exist!'})

    
        
class Home(BaseHandler):
    @tornado.web.authenticated    
    def get(self):
        self.write(
        self.render_template('home.html',
                {"user": tornado.escape.xhtml_escape(self.current_user)}))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/register", Register),
        (r"/login", Login),
        (r"/home", Home),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"})
    ],
    autoreload=True, 
    cookie_secret='2732736726', 
    login_url="/login")

if __name__ == "__main__":
    app = make_app()
    app.listen(8889)
    tornado.ioloop.IOLoop.current().start()