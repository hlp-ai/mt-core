import inspect

import tensorflow as tf

import yimt


class APITest(tf.test.TestCase):
    def testSubmodules(self):
        def _check(module):
            self.assertTrue(inspect.ismodule(module))

        _check(yimt.data)
        _check(yimt.decoders)
        _check(yimt.encoders)
        _check(yimt.inputters)
        _check(yimt.layers)
        _check(yimt.models)
        _check(yimt.optimizers)
        # _check(yimt.schedules)
        _check(yimt.tokenizers)
        _check(yimt.utils)


if __name__ == "__main__":
    tf.test.main()
