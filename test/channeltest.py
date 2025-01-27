#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2018 John Markus Bjørndalen, jmb@cs.uit.no.
See LICENSE.txt for licensing details (MIT License).
"""
import asyncio
from common import handle_common_args
from apycsp import process, BufferedChannel, Channel, ChannelPoisonException, poisonChannel, run_CSP
# from apycsp.plugNplay import *

handle_common_args()

N = 5


@process
async def WN(pid, cout):
    for i in range(N):
        print("  [%s] Writing %d" % (pid, i))
        await cout(i)
        await asyncio.sleep(0.1)
    print("Writer [%s] wrote all" % pid)
    await poisonChannel(cout)


@process
async def RN(pid, cin):
    for _ in range(N):
        v = await cin()
        print("  [%s] Reading %d" % (pid, v))
        await asyncio.sleep(0.1)
    print("Reader [%s] got all" % pid)
    await poisonChannel(cin)


# TODO: Robert
@process
async def FastWN(pid, cout):
    for i in range(50):
        print("  [%s] Writing %d" % (pid, i))
        await cout(i)
        # await asyncio.sleep(0.1)
    print("Writer [%s] wrote all" % pid)
    await poisonChannel(cout)


# TODO: Robert
@process
async def FastRN(pid, cin):
    try:
        while 1:
            v = await cin()
            print("  [%s] Reading %d" % (pid, v))
    except ChannelPoisonException:
        print('Reader [%s] caught poison exception' % pid)


def o2otest():
    print("-----------------------")
    print("Testing One2One Channel")
    print("Reader and writer should both report as done")
    c = Channel()
    run_CSP(WN(1, c.write),
            RN(2, c.read))


def o2atest():
    print("-----------------------")
    print("Testing One2Any Channel")
    print("Writer should report as done, none of the readers should")
    c = Channel()
    run_CSP(WN(1, c.write),
            RN(2, c.read),
            RN(3, c.read))


def a2otest():
    print("-----------------------")
    print("Testing Any2One Channel")
    print("Reader should report as done, none of the writers should")
    c = Channel()
    run_CSP(WN(1, c.write),
            WN(2, c.write),
            RN(3, c.read))


def a2atest():
    print("-----------------------")
    print("Testing Any2Any Channel")
    print("All readers and writers should report as done")
    # TODO: potential race if one of the writers/readers finish early and poison the channel!
    # the same problem might occur above as well!
    c = Channel()
    run_CSP(WN(1, c.write),
            WN(2, c.write),
            RN(3, c.read),
            RN(4, c.read))


def bo2otest():
    print("-----------------------")
    print("Testing BufferedOne2One Channel")
    print("Reader and writer should both report as done")
    c = BufferedChannel()
    run_CSP(FastWN(1, c.write),
            FastRN(2, c.read))


o2otest()
o2atest()
a2otest()
a2atest()
bo2otest()
