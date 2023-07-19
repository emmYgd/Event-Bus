from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver
from thespian.actors import *

class EventMessage(object):
    def __init__(self, event: str):
        self.event = event

class EventProtocol(LineReceiver):
    def __init__(self, actor):
        self.actor = actor

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
        Parses the received event and sends it to the event actor.

        Args:
            line: A line of data received from the event server.
        """
        event = line.decode()
        self.actor.send(EventMessage(event))

class EventActor(Actor):
    def receiveMessage(self, message: Any, sender: ActorAddress) -> None:
        if isinstance(message, EventMessage):
            self.handleEvent(message.event)

    def handleEvent(self, event):
        """Process the received event."""
        print(f"Received event: {event}")
        # Process the event as needed

class EventClientFactory(protocol.ClientFactory):
    def __init__(self, actor):
        self.actor = actor

    def buildProtocol(self, addr):
        """
        Called when the connection to the event server is established.
        Returns an instance of the EventProtocol.

        Args:
            addr: The address of the event server.

        Returns:
            An instance of EventProtocol.
        """
        return EventProtocol(self.actor)

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

class EventSystem:
    def __init__(self):
        self.actor_system = ActorSystem("multiprocQueueBase")
        self.actor = self.actor_system.createActor(EventActor)

    def sendEvent(self, event):
        """Send an event to the event server."""
        self.actor_system.tell(self.actor, EventMessage(event))

def main():
    event_system = EventSystem()

    # Create a TCP client factory with the event actor
    factory = EventClientFactory(event_system.actor)
    reactor.connectTCP("event-server-address", 1234, factory)

    # Send an event to the server
    reactor.callLater(0, event_system.sendEvent, "sample event to send")

    reactor.run()

    # Clean up the actor system
    event_system.actor_system.shutdown()

if __name__ == "__main__":
    main()
