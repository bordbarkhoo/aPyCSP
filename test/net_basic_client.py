#!/usr/bin/env python3
import time
import common
import apycsp
import apycsp.net
import asyncio

args = common.handle_common_args([
    (("-s", "--serv"), dict(help="specify server as host:port (use multiple times for multiple servers)", action="append", default=[]))
])
if len(args.serv) < 1:
    apycsp.net.setup_client()
else:
    for sp in args.serv:
        apycsp.net.setup_client(sp)

loop = asyncio.get_event_loop()
apycsp.net.send_message_sync({'op' : 'ping'})
apycsp.net.send_message_sync({'op' : 'print', 'args' : 'foo\nbar'})


@apycsp.process
async def reader(ch):
    for _ in range(10):
        print("About to read")
        ret = await ch.read()
        print(" - got message", ret)

rchan1 = apycsp.net.get_channel_proxy_s('net_t1')

print("Simple experiment")
loop.run_until_complete(reader(rchan1))


def measure_rt(print_hdr=True):
    if print_hdr:
        print("\n--------------------------- ")
        print("Measuring remote op roundtrip time")
    N = 1000
    t1 = time.time()
    for _ in range(N):
        apycsp.net.send_message_sync({'op' : 'ping'})
    t2 = time.time()
    dt_ms = (t2 - t1) * 1000
    us_msg = 1000 * dt_ms / N
    print(f"  - sending {N} messages took {dt_ms} ms")
    print(f"  - us per message : {us_msg}")


def measure_ch_read(print_hdr=True):
    if print_hdr:
        print("\n--------------------------- ")
        print("Reading from remote channel")

    @apycsp.process
    async def _reader(rchan, N):
        tot = 0
        for _ in range(N):
            v = await rchan.read()
            tot += v
        if tot != 42 * N:
            print("Total not the expected value", tot, 42 * N)

    N = 1000
    t1 = time.time()
    rchan = apycsp.net.get_channel_proxy_s('net_t2')
    loop.run_until_complete(_reader(rchan, N))
    t2 = time.time()
    dt_ms = (t2 - t1) * 1000
    us_msg = 1000 * dt_ms / N
    print(f"  - read {N} messages took {dt_ms} ms")
    print(f"  - us per message : {us_msg}")


for i in range(5):
    measure_rt(i == 0)
for i in range(5):
    measure_ch_read(i == 0)
