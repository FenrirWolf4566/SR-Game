import asyncio
from . import test_monkey_client
from . import test_server
import unittest

# run with "python3 -m tests" from the root directory
if __name__ == '__main__':
    unittest.main(module=test_server)
    #unittest.main(module=test_monkey_client)
    asyncio.run(test_monkey_client.test_monkey())
