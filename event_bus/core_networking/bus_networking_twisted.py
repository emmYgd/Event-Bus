from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver

class EventProtocol(LineReceiver):
    def connectionMade(self):
        """
        Called when a connection is made to the event server.
        """
        print("Connected to event server")

    def connectionLost(self, reason):
        """
        Called when the connection to the event server is lost.
        """
        print("Disconnected from event server")

    def lineReceived(self, line):
        """
        Called when a line of data is received from the event server.
        Parses the received event and calls the handleEvent method to process it.

        Args:
            line: A line of data received from the event server.
        """
        event = line.decode()
        self.handleEvent(event)

    def handleEvent(self, event):
        """
        Process the received event.

        Args:
            event: The event received from the event server.
        """
        print(f"Received event: {event}")
        # Process the event as needed

    def sendEvent(self, event):
        """
        Send an event to the event server.

        Args:
            event: The event to be sent to the event server.
        """
        self.sendLine(event.encode())

class EventClientFactory(protocol.ClientFactory):
    def __init__(self, event):
        self.event = event

    def buildProtocol(self, addr):
        """
        Called when the connection to the event server is established.
        Returns an instance of the EventProtocol.

        Args:
            addr: The address of the event server.

        Returns:
            An instance of EventProtocol.
        """
        protocol = EventProtocol()
        protocol.handleEvent = self.handleEvent
        return protocol

    def handleEvent(self, event):
        """
        Process the received event from the server.

        Args:
            event: The event received from the event server.
        """
        print(f"Received event from server: {event}")
        # Process the event as needed

    def startedConnecting(self, connector):
        """
        Called when a connection attempt starts.
        """
        print("Connecting to event server...")

    def clientConnectionFailed(self, connector, reason):
        """
        Called when a connection attempt fails.

        Args:
            connector: The connector used for the connection attempt.
            reason: The reason for the connection failure.
        """
        print("Connection failed.")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        """
        Called when an established connection is lost.

        Args:
            connector: The connector used for the connection.
            reason: The reason for the connection loss.
        """
        print("Connection lost.")
        reactor.stop()

    def sendEvent(self, event):
        """
        Send an event to the event server.

        Args:
            event: The event to be sent to the event server.
        """
        if hasattr(self, "protocol"):
            self.protocol.sendEvent(event)

def main():
    # Connect to the event server
    factory = EventClientFactory(event="sample event")
    reactor.connectTCP("event-server-address", 1234, factory)

    # Send an event to the server
    reactor.callLater(0, factory.sendEvent, "sample event to send")

    reactor.run()

if __name__ == "__main__":
    main()
