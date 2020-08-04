#from project import app
from project import create_app

# this needs to look more like Corey's code. You can't have all that stuff
# under if name == main. I think gunicorn gets passed an attirbute from above there...


pimt_app = create_app()

if __name__ == '__main__':
    pimt_app.run()


