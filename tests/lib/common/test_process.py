"""This is the module that tests process.py.
"""

import random
import sys
from logging import getLogger

import numpy as np
import tensorflow as tf

from lib.common import process
from lib.common.types import ParamKey as K
from lib.common.types import ParamLog
from lib.model.setup import SetupModel

sys.path.append('../tests')
from define import DATA_RESULT_DPATH, Layer

PARAM_LOG = ParamLog()
LOGGER = getLogger(name=PARAM_LOG.NAME)


class TestRecursiveReplace:
    """Tests :func:`process.recursive_replace`.
    """
    params = {
        'aaa': None,
        'bbb': {
            'ccc': (None, None),
        },
        'ddd': {
            'eee': [None],
            'fff': {
                'ggg': None,
            },
        },
    }

    def test(self):
        """Tests that no errors are raised.

        *   The replaced value must match the inverse replaced value.
        """
        data = process.recursive_replace(data=self.params, fm_val=None, to_val='None')
        print(f'{data=}')
        data = process.recursive_replace(data=self.params, fm_val='None', to_val=None)
        assert self.params == data


class TestSecToHMS:
    """Tests :func:`process.sec_to_hms`.
    """
    def test(self):
        """Tests that no errors are raised.

        *   Seconds can be converted to hours, minutes, seconds, and milliseconds.
        """
        hours = 1
        minutes = 10
        seconds = 30
        miliseconds = 0.123
        t = hours * 3600 + minutes * 60 + seconds + miliseconds
        hh, mm, ss, ms = process.sec_to_hms(time=t)
        assert hours == hh
        assert minutes == mm
        assert seconds == ss
        assert miliseconds == round(number=ms, ndigits=3)


class TestFixRandomSeed:
    """Tests :func:`process.fix_random_seed`.
    """

    def test(self):
        """Tests that no errors are raised.

        *   The random number seed is fixed.
        """
        # random
        process.fix_random_seed(seed=0)
        before = random.randint(0, 10)
        process.fix_random_seed(seed=0)
        after = random.randint(0, 10)
        print(f'{before=}, {after=}')
        assert before == after

        # np.random
        process.fix_random_seed(seed=0)
        before = np.random.randint(0, 10)
        process.fix_random_seed(seed=0)
        after = np.random.randint(0, 10)
        print(f'{before=}, {after=}')
        assert before == after

        # tf.random
        process.fix_random_seed(seed=0)
        before = tf.random.uniform(shape=[1], minval=0, maxval=10)
        process.fix_random_seed(seed=0)
        after = tf.random.uniform(shape=[1], minval=0, maxval=10)
        print(f'{before=}, {after=}')
        assert before == after


class TestSetWeight:
    """Tests :func:`process.set_weight`.
    """
    params = {
        K.EAGER: False,
        K.RESULT: DATA_RESULT_DPATH,
        K.MODEL: {K.KIND: 'simple'},
        K.LAYER: {
            K.KIND: ['flatten', 'dense_1', 'relu', 'dense_2'],
            'flatten': Layer.FLATTEN,
            'dense_1': Layer.DENSE_1,
            'dense_2': Layer.DENSE_2,
            'relu': Layer.RELU,
        },
        K.CLASSES: {
            K.OPT: '',
            K.LOSS: '',
            K.METRICS: [''],
        },
        K.INPUT_SHAPE: [28, 28, 1],
    }

    def test(self):
        """Tests that no errors are raised.

        *   The initialization weights are replaced by the trained weights.
        """
        process.fix_random_seed(seed=0)
        model = SetupModel(params=self.params).setup()

        process.fix_random_seed(seed=0)
        weighted_model = SetupModel(params=self.params).setup()
        weighted_model = process.set_weight(params=self.params, model=weighted_model)

        for m, w_m in zip(model.layers, weighted_model.layers):
            if m.get_weights():
                for m_weight, w_m_weight in zip(m.get_weights(), w_m.get_weights()):
                    print(np.where(m_weight != w_m_weight))
                    print(f'{m_weight=}')
                    print(f'{w_m_weight=}')
                    assert (m_weight != w_m_weight).any()
