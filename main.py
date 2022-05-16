import io
import sys
import jack
import socket
import threading

BLOCKSIZE = 256
PACKET_SIZE = 4 * BLOCKSIZE
CHANNELS = 2
PORT_IN = 42900
PORT_OUT = PORT_IN + CHANNELS
SOCK_IP = "127.0.0.1"

client = jack.Client("Thingy")
client.blocksize = BLOCKSIZE

# Flip if side B
if len(sys.argv) > 1 and sys.argv[1].lower() == "b":
    print("Using side B")
    PORT_IN, PORT_OUT = PORT_OUT, PORT_IN
else:
    print("Using side A")

if client.status.server_started:
    print("JACK server started")
if client.status.name_not_unique:
    print("unique name {0!r} assigned".format(client.name))


shutdown_event = threading.Event()

sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socks_in = []

for i in range(CHANNELS):
    client.inports.register(f"IN_{i}")
    client.outports.register(f"OUT_{i}")

    sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_in.bind((SOCK_IP, PORT_IN + i))
    sock_in.setblocking(False)
    socks_in.append(sock_in)


@client.set_process_callback
def process(frames):
    assert frames == client.blocksize
    assert client.blocksize == BLOCKSIZE

    for i, inp in enumerate(client.inports):
        buf = inp.get_buffer()
        sock_out.sendto(buf, (SOCK_IP, PORT_OUT + i))

    for i, out in enumerate(client.outports):
        try:
            buf = socks_in[i].recv(PACKET_SIZE)
            out.get_buffer()[:] = buf
        except io.BlockingIOError:
            pass


@client.set_blocksize_callback
def blocksize(blocksize):
    print("setting blocksize to", blocksize)


@client.set_shutdown_callback
def shutdown(status, reason):
    print("JACK shutdown!")
    print("status:", status)
    print("reason:", reason)
    shutdown_event.set()


@client.set_xrun_callback
def xrun(delay):
    print("xrun; delay", delay, "microseconds")


with client:
    print("Press Ctrl+C to stop")
    try:
        shutdown_event.wait()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
