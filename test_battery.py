# test_battery.py
# Unit tests for battery.py
# Author: Ayden Wayman

import pytest
from battery import Battery
from unittest.mock import Mock

@pytest.fixture
def charged_battery():
    """Battery at full capacity"""
    return Battery(100)

@pytest.fixture
def partially_charged_battery():
    """Battery at 70% charge"""
    b = Battery(100)
    b.mCharge = 70
    return b

@pytest.fixture
def empty_battery():
    """Battery at 0% charge"""
    b = Battery(100)
    b.mCharge = 0
    return b

def describe_battery():
    """Test suite for Battery class"""

    def describe_constructor():
        """Test battery initialization"""

        def it_initializes_with_full_charge():
            battery = Battery(100)
            assert battery.getCapacity() == 100
            assert battery.getCharge() == 100

        def it_initializes_with_external_monitor():
            mock_monitor = Mock()
            battery = Battery(100, external_monitor=mock_monitor)
            assert battery.external_monitor == mock_monitor

    def describe_getCapacity():
        """Test getCapacity method"""

        def it_returns_correct_capacity(charged_battery):
            assert charged_battery.getCapacity() == 100

        def it_returns_capacity_for_nonstandard_values():
            battery = Battery(250)
            assert battery.getCapacity() == 250

    def describe_getCharge():
        """Test getCharge method"""

        def it_returns_full_charge_initially(charged_battery):
            assert charged_battery.getCharge() == 100

        def it_returns_partial_charge(partially_charged_battery):
            assert partially_charged_battery.getCharge() == 70

        def it_returns_zero_charge(empty_battery):
            assert empty_battery.getCharge() == 0

    def describe_recharge():
        """Test recharge method - state changes"""

        def it_increases_charge_with_valid_amount(partially_charged_battery):
            result = partially_charged_battery.recharge(20)
            assert result is True
            assert partially_charged_battery.getCharge() == 90

        def it_caps_charge_at_capacity(partially_charged_battery):
            result = partially_charged_battery.recharge(50)
            assert result is True
            assert partially_charged_battery.getCharge() == 100

        def it_does_not_exceed_capacity(charged_battery):
            result = charged_battery.recharge(10)
            assert result is False
            assert charged_battery.getCharge() == 100

        def it_recharges_from_empty(empty_battery):
            result = empty_battery.recharge(30)
            assert result is True
            assert empty_battery.getCharge() == 30

        def it_returns_false_for_zero_amount(partially_charged_battery):
            result = partially_charged_battery.recharge(0)
            assert result is False
            assert partially_charged_battery.getCharge() == 70

        def it_returns_false_for_negative_amount(partially_charged_battery):
            result = partially_charged_battery.recharge(-10)
            assert result is False
            assert partially_charged_battery.getCharge() == 70

        def it_returns_false_when_already_full(charged_battery):
            result = charged_battery.recharge(10)
            assert result is False
            assert charged_battery.getCharge() == 100

    def describe_recharge_with_monitor():
        """Test recharge method - external monitor interactions"""

        def it_calls_monitor_on_recharge(partially_charged_battery):
            # setup
            mock_monitor = Mock()
            battery = partially_charged_battery
            battery.external_monitor = mock_monitor

            # execute
            battery.recharge(20)   # battery starts at 70, add 20

            # validate
            mock_monitor.notify_recharge.assert_called_once_with(90)

        def it_calls_monitor_with_capped_value(partially_charged_battery):
            mock_monitor = Mock()
            partially_charged_battery.external_monitor = mock_monitor

            partially_charged_battery.recharge(50)  # 70 + 50 = 120, capped at 100

            mock_monitor.notify_recharge.assert_called_once_with(100)

        def it_calls_monitor_from_empty(empty_battery):
            mock_monitor = Mock()
            empty_battery.external_monitor = mock_monitor

            empty_battery.recharge(25)

            mock_monitor.notify_recharge.assert_called_once_with(25)

        def it_does_not_call_monitor_without_monitor_set(partially_charged_battery):
            # No monitor attached
            result = partially_charged_battery.recharge(20)
            
            # Should succeed without error
            assert result is True
            assert partially_charged_battery.getCharge() == 90

        def it_does_not_call_monitor_on_invalid_recharge(partially_charged_battery):
            mock_monitor = Mock()
            partially_charged_battery.external_monitor = mock_monitor

            partially_charged_battery.recharge(0)  # Invalid amount

            mock_monitor.notify_recharge.assert_not_called()

        def it_does_not_call_monitor_on_negative_recharge(partially_charged_battery):
            mock_monitor = Mock()
            partially_charged_battery.external_monitor = mock_monitor

            partially_charged_battery.recharge(-10)  # Invalid amount

            mock_monitor.notify_recharge.assert_not_called()

    def describe_drain():
        """Test drain method - state changes"""

        def it_decreases_charge_with_valid_amount(partially_charged_battery):
            result = partially_charged_battery.drain(20)
            assert result is True
            assert partially_charged_battery.getCharge() == 50

        def it_prevents_charge_below_zero(partially_charged_battery):
            result = partially_charged_battery.drain(80)
            assert result is True
            assert partially_charged_battery.getCharge() == 0

        def it_drains_to_exactly_zero(partially_charged_battery):
            result = partially_charged_battery.drain(70)
            assert result is True
            assert partially_charged_battery.getCharge() == 0

        def it_returns_false_for_zero_amount(partially_charged_battery):
            result = partially_charged_battery.drain(0)
            assert result is False
            assert partially_charged_battery.getCharge() == 70

        def it_returns_false_for_negative_amount(partially_charged_battery):
            result = partially_charged_battery.drain(-10)
            assert result is False
            assert partially_charged_battery.getCharge() == 70

        def it_returns_false_when_already_empty(empty_battery):
            result = empty_battery.drain(10)
            assert result is False
            assert empty_battery.getCharge() == 0

        def it_drains_fully_charged_battery(charged_battery):
            result = charged_battery.drain(30)
            assert result is True
            assert charged_battery.getCharge() == 70

    def describe_drain_with_monitor():
        """Test drain method - external monitor interactions"""

        def it_calls_monitor_on_drain(partially_charged_battery):
            mock_monitor = Mock()
            partially_charged_battery.external_monitor = mock_monitor

            partially_charged_battery.drain(20)  # 70 - 20 = 50

            mock_monitor.notify_drain.assert_called_once_with(50)

        def it_calls_monitor_with_floored_value(partially_charged_battery):
            mock_monitor = Mock()
            partially_charged_battery.external_monitor = mock_monitor

            partially_charged_battery.drain(80)  # 70 - 80 = -10, floored at 0

            mock_monitor.notify_drain.assert_called_once_with(0)

        def it_calls_monitor_when_draining_to_zero(partially_charged_battery):
            mock_monitor = Mock()
            partially_charged_battery.external_monitor = mock_monitor

            partially_charged_battery.drain(70)  # Exact amount

            mock_monitor.notify_drain.assert_called_once_with(0)

        def it_calls_monitor_from_full_charge(charged_battery):
            mock_monitor = Mock()
            charged_battery.external_monitor = mock_monitor

            charged_battery.drain(25)

            mock_monitor.notify_drain.assert_called_once_with(75)

        def it_does_not_call_monitor_without_monitor_set(partially_charged_battery):
            # No monitor attached
            result = partially_charged_battery.drain(20)
            
            # Should succeed without error
            assert result is True
            assert partially_charged_battery.getCharge() == 50

        def it_does_not_call_monitor_on_invalid_drain(partially_charged_battery):
            mock_monitor = Mock()
            partially_charged_battery.external_monitor = mock_monitor

            partially_charged_battery.drain(0)  # Invalid amount

            mock_monitor.notify_drain.assert_not_called()

        def it_does_not_call_monitor_on_negative_drain(partially_charged_battery):
            mock_monitor = Mock()
            partially_charged_battery.external_monitor = mock_monitor

            partially_charged_battery.drain(-10)  # Invalid amount

            mock_monitor.notify_drain.assert_not_called()

    def describe_edge_cases():
        """Test edge cases and complex scenarios"""

        def it_handles_multiple_recharges_with_monitor():
            battery = Battery(100)
            battery.mCharge = 50
            mock_monitor = Mock()
            battery.external_monitor = mock_monitor

            battery.recharge(10)
            battery.recharge(15)
            battery.recharge(20)

            assert battery.getCharge() == 95
            assert mock_monitor.notify_recharge.call_count == 3
            calls = [call[0][0] for call in mock_monitor.notify_recharge.call_args_list]
            assert calls == [60, 75, 95]

        def it_handles_multiple_drains_with_monitor():
            battery = Battery(100)
            mock_monitor = Mock()
            battery.external_monitor = mock_monitor

            battery.drain(10)
            battery.drain(20)
            battery.drain(30)

            assert battery.getCharge() == 40
            assert mock_monitor.notify_drain.call_count == 3
            calls = [call[0][0] for call in mock_monitor.notify_drain.call_args_list]
            assert calls == [90, 70, 40]

        def it_handles_alternating_recharge_and_drain():
            battery = Battery(100)
            battery.mCharge = 50
            mock_monitor = Mock()
            battery.external_monitor = mock_monitor

            battery.recharge(20)
            battery.drain(10)
            battery.recharge(15)
            battery.drain(25)

            assert battery.getCharge() == 50
            assert mock_monitor.notify_recharge.call_count == 2
            assert mock_monitor.notify_drain.call_count == 2

        def it_maintains_capacity_after_operations(charged_battery):
            original_capacity = charged_battery.getCapacity()
            
            charged_battery.drain(30)
            charged_battery.recharge(20)
            charged_battery.drain(10)
            
            assert charged_battery.getCapacity() == original_capacity
