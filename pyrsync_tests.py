import unittest
import hashlib
import math

from io import BytesIO

import pyrsync


class PyRsyncTests(unittest.TestCase):
    TEST_BLOCK_SIZE = 4
    TEST_FILE_1 = b'one really small file here'

    def get_block(self, data, block):
        return data[
            block * self.TEST_BLOCK_SIZE:(block + 1) * self.TEST_BLOCK_SIZE
        ]

    def test_blockchecksums(self):
        with BytesIO(self.TEST_FILE_1) as file1:
            hashes = pyrsync.blockchecksums(
                file1,
                blocksize=self.TEST_BLOCK_SIZE
            )

            for block, block_hash in enumerate(hashes):
                block_data = self.get_block(self.TEST_FILE_1, block)

                weaksum = pyrsync.weakchecksum(block_data)[0]
                strongsum = hashlib.md5(block_data).digest()

                self.assertEqual(block_hash, (weaksum, strongsum))

    def test_rsyncdelta_same_file(self):
        with BytesIO(self.TEST_FILE_1) as file_to:
            hashes = pyrsync.blockchecksums(
                file_to,
                blocksize=self.TEST_BLOCK_SIZE
            )

            with BytesIO(self.TEST_FILE_1) as file_from:
                delta = pyrsync.rsyncdelta(
                    file_from, hashes,
                    blocksize=self.TEST_BLOCK_SIZE
                )

                for index, block in enumerate(delta):
                    self.assertEqual(index, block)

    def test_rsyncdelta_with_changes(self):
        changes_in_blocks = [
            (0, 0),
            (3, 2),
            (4, 0),
            (5, self.TEST_BLOCK_SIZE - 1),
            (math.ceil(len(self.TEST_FILE_1) / self.TEST_BLOCK_SIZE) - 1, 0)
        ]
        changed_blocks = [block for block, position in changes_in_blocks]

        with BytesIO(self.TEST_FILE_1) as changed_file:
            file_buffer = changed_file.getbuffer()

            for block, position in changes_in_blocks:
                file_buffer[block * self.TEST_BLOCK_SIZE + position] += 1

            changed_file_data = changed_file.getvalue()

            with BytesIO(self.TEST_FILE_1) as file_to:
                hashes = pyrsync.blockchecksums(
                    file_to,
                    blocksize=self.TEST_BLOCK_SIZE
                )

                delta = pyrsync.rsyncdelta(
                    changed_file, hashes,
                    blocksize=self.TEST_BLOCK_SIZE,
                    max_buffer=self.TEST_BLOCK_SIZE
                )
                delta=list(delta)
                for block, data in enumerate(delta):
                    if block in changed_blocks:
                        self.assertEqual(
                            self.get_block(changed_file_data, block),
                            data
                        )
                    else:
                        self.assertEqual(block, data)

if __name__ == '__main__':
    unittest.main()
