import socketio
from PyQt5.QtCore import pyqtSignal, QObject

class StreamElementsClient(QObject):
    giftedSubs = pyqtSignal(int)
    bits = pyqtSignal(int)
    resub = pyqtSignal()
    finished = pyqtSignal()
    def __init__(self, jwt):
        super().__init__()
        self.jwt = jwt
        # Initialize the Socket.IO client
        self.sio = socketio.Client()
        
        # Connect events to class methods
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('authenticated', self.on_authenticated)
        self.sio.on('unauthorized', self.on_unauthorized)
        self.sio.on('event', self.on_event)

    def close(self):
        self.disconnect()

    def change(self,jwt):
        if(jwt==self.jwt):
            return
        self.disconnect()
        self.jwt = jwt
        self.connect()    

    def connect(self):
        # Connect to the server
        print("connect")
        self.sio.connect('https://realtime.streamelements.com', transports=['websocket'])

    def disconnect(self):
        # Disconnect from the server
        self.sio.disconnect()

    def authenticate_jwt(self):
        # Authenticate with JWT method
        self.sio.emit('authenticate', {'method': 'jwt', 'token': self.jwt})

    def on_connect(self):
        print('Successfully connected to the websocket')
        self.authenticate_jwt()  # You can switch to authenticate_jwt() if needed

    def on_disconnect(self):
        print('Disconnected from websocket')
        # Reconnect or handle reconnection here

    def on_authenticated(self, data):
        channel_id = data['channelId']
        print(f'Successfully connected to channel {channel_id}')

    def on_unauthorized(self, data):
        print(data)

    def on_event(self, data,ts):
        if(data["type"]=='subscriber'):
            if(data["data"].get("gifted",False) ):
                return
            self.resub.emit()
        elif(data["type"]=='communityGiftPurchase'):
            amount = int(data["data"]["amount"])
            self.giftedSubs.emit(amount)

        elif(data["type"]=='cheer'):
            amount = int(data["data"]["amount"])
            self.bits.emit(amount)
        # print(data)
        