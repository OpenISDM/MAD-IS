from mad_interface_server import app
import socket
# import socket
app.run(host= socket.gethostbyname(socket.gethostname()), port=int("80"), debug=True)
# app.run(host=socket.gethostbyname(socket.gethostname()),
        # port=int("80"), debug=True)
