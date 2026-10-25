import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.device_status import DeviceStatus
from models.projector_remote import ProjectorRemote
from models.air_conditioner_remote import AirConditionerRemote
from models.wireless_microphone import WirelessMicrophone
from exceptions.device_exceptions import DeviceNotReadyException, DeviceOperationException


class TestDevices(unittest.TestCase):
    def test_projector_remote_readiness_and_score(self):
        # Mức pin < 20: không sẵn sàng
        p_low = ProjectorRemote("PR01", "Remote Sony", "Kho A", battery_level=15)
        self.assertFalse(p_low.is_ready_for_use())
        self.assertEqual(p_low.get_default_priority_score(), 15.0)

        # Mức pin >= 20: sẵn sàng
        p_ok = ProjectorRemote("PR02", "Remote Panasonic", "Kho A", battery_level=75)
        self.assertTrue(p_ok.is_ready_for_use())
        self.assertEqual(p_ok.get_default_priority_score(), 75.0)

        # Mức pin không hợp lệ
        with self.assertRaises(ValueError):
            ProjectorRemote("PR03", "Remote Lỗi", "Kho A", battery_level=120)

    def test_air_conditioner_remote_compatibility_and_readiness(self):
        ac = AirConditionerRemote("AC01", "Remote Daikin", "Kho B", compatible_rooms={"A101", "A102"})
        self.assertTrue(ac.is_ready_for_use())
        self.assertTrue(ac.is_compatible_with("A101"))
        self.assertTrue(ac.is_compatible_with("A102"))
        self.assertFalse(ac.is_compatible_with("B201"))
        self.assertEqual(ac.get_default_priority_score(), 100.0)

    def test_wireless_microphone_readiness_and_score(self):
        # Pin < 30 -> Không sẵn sàng
        m_low_pin = WirelessMicrophone("WM01", "Mic Shure 1", "Kho C", battery_level=20, signal_quality=80)
        self.assertFalse(m_low_pin.is_ready_for_use())

        # Sóng < 40 -> Không sẵn sàng
        m_low_signal = WirelessMicrophone("WM02", "Mic Shure 2", "Kho C", battery_level=50, signal_quality=30)
        self.assertFalse(m_low_signal.is_ready_for_use())

        # Pin >= 30 và Sóng >= 40 -> Sẵn sàng
        m_ok = WirelessMicrophone("WM03", "Mic Sennheiser", "Kho C", battery_level=80, signal_quality=90)
        self.assertTrue(m_ok.is_ready_for_use())
        # Điểm ưu tiên là trung bình cộng: (80 + 90) / 2 = 85.0
        self.assertEqual(m_ok.get_default_priority_score(), 85.0)

    def test_borrow_and_return_lifecycle(self):
        device = ProjectorRemote("PR10", "Remote Test", "Kho A", battery_level=80)
        self.assertEqual(device.status, DeviceStatus.AVAILABLE)

        # Mượn thành công
        device.borrow()
        self.assertEqual(device.status, DeviceStatus.BORROWED)
        self.assertFalse(device.is_ready_for_use())

        # Không thể mượn lại khi đang Borrowed
        with self.assertRaises(DeviceNotReadyException):
            device.borrow()

        # Trả thiết bị về kho
        device.return_device()
        self.assertEqual(device.status, DeviceStatus.AVAILABLE)
        self.assertTrue(device.is_ready_for_use())

        # Không thể trả khi thiết bị đang ở trạng thái Available
        with self.assertRaises(DeviceOperationException):
            device.return_device()


if __name__ == "__main__":
    unittest.main()
