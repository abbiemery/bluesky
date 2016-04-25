import warnings
import pytest
from bluesky.callbacks import collector, CallbackCounter
from bluesky.plans import (AbsListScanPlan, AbsScanPlan, LogAbsScanPlan,
                           DeltaListScanPlan, DeltaScanPlan, LogDeltaScanPlan,
                           AdaptiveAbsScanPlan, AdaptiveDeltaScanPlan, Count,
                           OuterProductAbsScanPlan, InnerProductAbsScanPlan,
                           OuterProductDeltaScanPlan, InnerProductDeltaScanPlan)

from bluesky import Msg
from bluesky.examples import motor, det, SynGauss, motor1, motor2
from bluesky.tests.utils import setup_test_run_engine
import asyncio
import time as ttime
import numpy as np
loop = asyncio.get_event_loop()

RE = setup_test_run_engine()


def traj_checker(scan, expected_traj):
    actual_traj = []
    callback = collector('motor', actual_traj)
    RE(scan, subs={'event': callback})
    assert actual_traj == list(expected_traj)


def multi_traj_checker(scan, expected_data):
    actual_data = []

    def collect_data(name, event):
        actual_data.append(event['data'])

    RE(scan, subs={'event': collect_data})
    assert actual_data == expected_data


def test_outer_product_ascan():
    motor.set(0)
    scan = OuterProductAbsScanPlan([det], motor1, 1, 3, 3, motor2, 10, 20, 2,
                               False)
    # Note: motor1 is the first motor specified, and so it is the "slow"
    # axis, matching the numpy convention.
    expected_data = [
        {'motor2': 10.0, 'det': 1.0, 'motor1': 1.0},
        {'motor2': 20.0, 'det': 1.0, 'motor1': 1.0},
        {'motor2': 10.0, 'det': 1.0, 'motor1': 2.0},
        {'motor2': 20.0, 'det': 1.0, 'motor1': 2.0},
        {'motor2': 10.0, 'det': 1.0, 'motor1': 3.0},
        {'motor2': 20.0, 'det': 1.0, 'motor1': 3.0}]
    multi_traj_checker(scan, expected_data)


def test_outer_product_ascan_snaked():
    motor.set(0)
    scan = OuterProductAbsScanPlan([det], motor1, 1, 3, 3, motor2, 10, 20, 2, True)
    # Note: motor1 is the first motor specified, and so it is the "slow"
    # axis, matching the numpy convention.
    expected_data = [
        {'motor2': 10.0, 'det': 1.0, 'motor1': 1.0},
        {'motor2': 20.0, 'det': 1.0, 'motor1': 1.0},
        {'motor2': 20.0, 'det': 1.0, 'motor1': 2.0},
        {'motor2': 10.0, 'det': 1.0, 'motor1': 2.0},
        {'motor2': 10.0, 'det': 1.0, 'motor1': 3.0},
        {'motor2': 20.0, 'det': 1.0, 'motor1': 3.0}]
    multi_traj_checker(scan, expected_data)


def test_inner_product_ascan():
    motor.set(0)
    scan = InnerProductAbsScanPlan([det], 3, motor1, 1, 3, motor2, 10, 30)
    # Note: motor1 is the first motor specified, and so it is the "slow"
    # axis, matching the numpy convention.
    expected_data = [
        {'motor2': 10.0, 'det': 1.0, 'motor1': 1.0},
        {'motor2': 20.0, 'det': 1.0, 'motor1': 2.0},
        {'motor2': 30.0, 'det': 1.0, 'motor1': 3.0}]
    multi_traj_checker(scan, expected_data)


def test_outer_product_dscan():
    scan = OuterProductDeltaScanPlan([det], motor1, 1, 3, 3, motor2, 10, 20, 2,
                                 False)
    # Note: motor1 is the first motor specified, and so it is the "slow"
    # axis, matching the numpy convention.
    motor.set(0)
    motor1.set(5)
    motor2.set(8)
    expected_data = [
        {'motor2': 18.0, 'det': 1.0, 'motor1': 6.0},
        {'motor2': 28.0, 'det': 1.0, 'motor1': 6.0},
        {'motor2': 18.0, 'det': 1.0, 'motor1': 7.0},
        {'motor2': 28.0, 'det': 1.0, 'motor1': 7.0},
        {'motor2': 18.0, 'det': 1.0, 'motor1': 8.0},
        {'motor2': 28.0, 'det': 1.0, 'motor1': 8.0}]
    multi_traj_checker(scan, expected_data)


def test_outer_product_dscan_snaked():
    scan = OuterProductDeltaScanPlan([det], motor1, 1, 3, 3, motor2, 10, 20, 2,
                                 True)
    # Note: motor1 is the first motor specified, and so it is the "slow"
    # axis, matching the numpy convention.
    motor.set(0)
    motor1.set(5)
    motor2.set(8)
    expected_data = [
        {'motor2': 18.0, 'det': 1.0, 'motor1': 6.0},
        {'motor2': 28.0, 'det': 1.0, 'motor1': 6.0},
        {'motor2': 28.0, 'det': 1.0, 'motor1': 7.0},
        {'motor2': 18.0, 'det': 1.0, 'motor1': 7.0},
        {'motor2': 18.0, 'det': 1.0, 'motor1': 8.0},
        {'motor2': 28.0, 'det': 1.0, 'motor1': 8.0}]
    multi_traj_checker(scan, expected_data)


def test_inner_product_dscan():
    motor.set(0)
    motor1.set(5)
    motor2.set(8)
    scan = InnerProductDeltaScanPlan([det], 3, motor1, 1, 3, motor2, 10, 30)
    # Note: motor1 is the first motor specified, and so it is the "slow"
    # axis, matching the numpy convention.
    expected_data = [
        {'motor2': 18.0, 'det': 1.0, 'motor1': 6.0},
        {'motor2': 28.0, 'det': 1.0, 'motor1': 7.0},
        {'motor2': 38.0, 'det': 1.0, 'motor1': 8.0}]
    multi_traj_checker(scan, expected_data)


def test_ascan():
    traj = [1, 2, 3]
    scan = AbsListScanPlan([det], motor, traj)
    traj_checker(scan, traj)


def test_dscan():
    traj = np.array([1, 2, 3])
    motor.set(-4)
    print(motor.read())
    scan = DeltaListScanPlan([det], motor, traj)
    traj_checker(scan, traj - 4)


def test_dscan_list_input():
    # GH225
    traj = [1, 2, 3]
    motor.set(-4)
    scan = DeltaListScanPlan([det], motor, traj)
    traj_checker(scan, np.array(traj) - 4)


def test_lin_ascan():
    traj = np.linspace(0, 10, 5)
    scan = AbsScanPlan([det], motor, 0, 10, 5)
    traj_checker(scan, traj)


def test_log_ascan():
    traj = np.logspace(0, 10, 5)
    scan = LogAbsScanPlan([det], motor, 0, 10, 5)
    traj_checker(scan, traj)


def test_lin_dscan():
    traj = np.linspace(0, 10, 5) + 6
    motor.set(6)
    scan = DeltaScanPlan([det], motor, 0, 10, 5)
    traj_checker(scan, traj)


def test_log_dscan():
    traj = np.logspace(0, 10, 5) + 6
    motor.set(6)
    scan = LogDeltaScanPlan([det], motor, 0, 10, 5)
    traj_checker(scan, traj)


def test_adaptive_ascan():
    scan1 = AdaptiveAbsScanPlan([det], 'det', motor, 0, 5, 0.1, 1, 0.1, True)
    scan2 = AdaptiveAbsScanPlan([det], 'det', motor, 0, 5, 0.1, 1, 0.2, True)
    scan3 = AdaptiveAbsScanPlan([det], 'det', motor, 0, 5, 0.1, 1, 0.1, False)

    actual_traj = []
    col = collector('motor', actual_traj)
    counter1 = CallbackCounter()
    counter2 = CallbackCounter()

    RE(scan1, subs={'event': [col, counter1]})
    RE(scan2, subs={'event': counter2})
    assert counter1.value > counter2.value
    assert actual_traj[0] == 0

    actual_traj = []
    col = collector('motor', actual_traj)
    RE(scan3, {'event': col})
    monotonic_increasing = np.all(np.diff(actual_traj) > 0)
    assert monotonic_increasing


def test_adaptive_dscan():
    scan1 = AdaptiveDeltaScanPlan([det], 'det', motor, 0, 5, 0.1, 1, 0.1, True)
    scan2 = AdaptiveDeltaScanPlan([det], 'det', motor, 0, 5, 0.1, 1, 0.2, True)
    scan3 = AdaptiveDeltaScanPlan([det], 'det', motor, 0, 5, 0.1, 1, 0.1, False)

    actual_traj = []
    col = collector('motor', actual_traj)
    counter1 = CallbackCounter()
    counter2 = CallbackCounter()

    motor.set(1)
    RE(scan1, subs={'event': [col, counter1]})
    RE(scan2, subs={'event': counter2})
    assert counter1.value > counter2.value
    assert actual_traj[0] == 1

    actual_traj = []
    col = collector('motor', actual_traj)
    RE(scan3, {'event': col})
    monotonic_increasing = np.all(np.diff(actual_traj) > 0)
    assert monotonic_increasing


def test_count():
    actual_intensity = []
    col = collector('det', actual_intensity)
    motor.set(0)
    scan = Count([det])
    RE(scan, subs={'event': col})
    assert actual_intensity[0] == 1.

    # multiple counts, via updating attribute
    actual_intensity = []
    col = collector('det', actual_intensity)
    scan = Count([det], num=3, delay=0.05)
    RE(scan, subs={'event': col})
    assert scan.num == 3
    assert actual_intensity == [1., 1., 1.]

    # multiple counts, via passing arts to __call__
    actual_intensity = []
    col = collector('det', actual_intensity)
    scan = Count([det], num=3, delay=0.05)
    RE(scan(num=2), subs={'event': col})
    assert actual_intensity == [1., 1.]
    # attribute should still be 3
    assert scan.num == 3
    actual_intensity = []
    col = collector('det', actual_intensity)
    RE(scan, subs={'event': col})
    assert actual_intensity == [1., 1., 1.]


def test_set():
    scan = AbsScanPlan([det], motor, 1, 5, 3)
    assert scan.start == 1
    assert scan.stop == 5
    assert scan.num == 3
    scan.set(start=2)
    assert scan.start == 2
    scan.set(num=4)
    assert scan.num == 4
    assert scan.start == 2


def test_wait_for():
    ev = asyncio.Event()

    def done():
        ev.set()
    scan = [Msg('wait_for', None, [ev.wait(), ]), ]
    loop.call_later(2, done)
    start = ttime.time()
    RE(scan)
    stop = ttime.time()
    assert stop - start >= 2


def test_pre_run_post_run():
    c = Count([])
    def f(x):
        yield Msg('HEY', None)
    c.pre_run = f
    list(c)[0].command == 'HEY'

    c = Count([])
    def f(x):
        yield Msg('HEY', None)
    c.pre_run = f
    list(c)[-1].command == 'HEY'
