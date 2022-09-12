import inspect

import tensorflow as tf

import yimt.core


class APITest(tf.test.TestCase):
    def testSubmodules(self):
        def _check(module):
            self.assertTrue(inspect.ismodule(module))

        _check(yimt.core.data)
        _check(yimt.core.decoders)
        _check(yimt.core.encoders)
        _check(yimt.core.inputters)
        _check(yimt.core.layers)
        _check(yimt.core.models)
        _check(yimt.core.optimizers)
        # _check(yimt.schedules)
        _check(yimt.core.tokenizers)
        _check(yimt.core.utils)


if __name__ == "__main__":
    tf.test.main()
