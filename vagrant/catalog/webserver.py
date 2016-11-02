from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


def create_db_connection(dbname):
    print "Attempting to connect to %s" % dbname
    engine = create_engine('sqlite:///%s' % dbname)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    print "Session established"
    return session

def get_all_restaurants():
    session = create_db_connection('restaurantmenu.db')
    all_restaurants = session.query(Restaurant).all()
    print "Retrieved all Restaurants"
    session.close()
    print "Session closed"
    return all_restaurants

def new_restaurant(resname):
    print "Function called with argument %s" % resname
    try:
        session = create_db_connection('restaurantmenu.db')
        print "Session initiated"
        newrestaurant = Restaurant(name=resname)
        print "Restaurant: %s" % resname
        session.add(newrestaurant)
        print "Session added"
        session.commit()
        print "Session committed"
        session.close()
        print "Restaurant %s added!" % resname
        return "Success"
    except:
        print "Could not add Restaurant: %s" % resname
        return "Failed"


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += '<html><body>'
                output += 'Hello!<br><a href="/hola">Say hola</a>'
                output += '<form method="POST" enctype="multipart/form-data" \
                            action="/hello"><h2>What would you like me to say? \
                            </h2><input name="message" type="text"><input \
                            type="submit" value="submit"> </form>'
                output += '</body></html>'
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += '<html><body>'
                output += 'Hola<br><a href="/hello">Say Hello</a>'
                output += '<form method="POST" enctype="multipart/form-data" \
                            action="/hello"><h2>What would you like me to say? \
                            </h2><input name="message" type="text"><input \
                            type="submit" value="submit"> </form>'
                output += '</body></html>'
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = get_all_restaurants()
                output = ""
                output += '<html><body>'
                output += '<a href="/restaurants/new">Create new restaurant</a><br><br>'
                for restaurant in restaurants:
                    output += restaurant.name
                    output += '<br>'
                    output += '<a href="#">Edit</a><br>'
                    output += '<a href="#">Delete</a><br><br>'
                output += '</body></html>'
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += '<html><body>'
                output += '<form method="POST" enctype="multipart/form-data" \
                            action="/restaurants"><h2>Enter a restaurant name \
                            </h2><input name="restaurant" type="text"><input \
                            type="submit" value="submit"> </form>'
                output += '</body></html>'

                self.wfile.write(output)
                print output

            if self.path.endswith("/restaurants/%d/edit"):
                pass

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/restaurants'):
                print "Adding restaurant"

                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurantname = fields.get('restaurant')

                if restaurantname:
                    print "Restaurant name found: %s" % restaurantname[0]
                    try:
                        result = new_restaurant(restaurantname[0])
                        print result
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end-headers()

                    except:
                        print "there was a problem and no restaurant was added"

            else:
                self.send_response(301)
                self.end_headers()
                print "Posted message"

                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                    if messagecontent:
                        output = ""
                        output += '<html><body>'
                        output += '<h2>Listen to this:</h2>'
                        output += '<h1> %s </h1>' % messagecontent[0]

                        output += '<form method="POST" enctype="multipart/form-data" \
                                    action="/hello"><h2>What would you like me to say? \
                                    </h2><input name="message" type="text"><input \
                                    type="submit" value="submit"> </form>'
                        output += '</body></html>'
                        self.wfile.write(output)
                        print output

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Server is running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " closing server"
        server.socket.close()
        print "Server successfully shut down"



if __name__ == '__main__':
    main()
