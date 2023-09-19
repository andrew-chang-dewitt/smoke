"""Testing the pub sub module."""

import asyncio
from time import sleep, time
from unittest import IsolatedAsyncioTestCase as TestCase, main

from smoke.pubsub import ChannelSPMCAsync, ChannelSPMCThreaded


class TestChannelSPMCAsync(TestCase):
    """Testing the async impl."""

    async def test_publish_many(self) -> None:
        res = []

        async def sub(arg: str) -> None:
            await asyncio.sleep(1)

            res.append(arg)

        async def long_sub(arg: str) -> None:
            await asyncio.sleep(2)

            res.append("long " + arg)

        chn: ChannelSPMCAsync[str, None] = ChannelSPMCAsync()

        chn.sub(sub)
        chn.sub(long_sub)
        chn.sub(sub)
        chn.sub(sub)
        chn.sub(sub)
        start = time()
        await chn.pub("Hello world")
        end = time()
        elapsed = end - start

        with self.subTest():
            actual = res.count("Hello world")
            self.assertEqual(actual, 4)

        with self.subTest():
            actual = res.count("long Hello world")
            self.assertEqual(actual, 1)

        with self.subTest():
            self.assertLessEqual(elapsed, 2.5)


class TestChannelSPMCThreaded(TestCase):
    """Testing the async impl."""

    def test_publish_many(self) -> None:
        res = []

        def sub(arg: str) -> None:
            sleep(1)

            res.append(arg)

        def long_sub(arg: str) -> None:
            sleep(2)

            res.append("long " + arg)

        chn: ChannelSPMCThreaded[str, None] = ChannelSPMCThreaded()

        chn.sub(sub)
        chn.sub(long_sub)
        chn.sub(sub)
        chn.sub(sub)
        chn.sub(sub)
        start = time()
        threads = chn.pub("Hello world")

        for thread in threads:
            thread.join()

        end = time()
        elapsed = end - start

        with self.subTest():
            actual = res.count("Hello world")
            self.assertEqual(actual, 4)

        with self.subTest():
            actual = res.count("long Hello world")
            self.assertEqual(actual, 1)

        with self.subTest():
            self.assertLessEqual(elapsed, 2.5)


if __name__ == "__main__":
    main()
