import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.device_status import DeviceStatus
from models.projector_remote import ProjectorRemote
from models.air_conditioner_remote import AirConditionerRemote
from models.wireless_microphone import WirelessMicrophone
from repositories.in_memory_repository import InMemoryRepository
from strategies.highest_priority_strategy import HighestPriorityStrategy
from strategies.first_available_strategy import FirstAvailableStrategy
from services.allocation_service import AllocationService
from exceptions.device_exceptions import DuplicateIdException, NoSuitableItemException


class TestAllocationService(unittest.TestCase):
    def setUp(self):
        # - 3 điều khiển máy chiếu có mức pin khác nhau: 10% (không sẵn sàng), 60%, 95%
        self.p_low = ProjectorRemote("PR01", "Remote Sony (Hết pin)", "Kho A", battery_level=10)
        self.p_mid = ProjectorRemote("PR02", "Remote Epson (Trung bình)", "Kho A", battery_level=60)
        self.p_high = ProjectorRemote("PR03", "Remote Panasonic (Pin tốt)", "Kho A", battery_level=95)

        # - 2 điều khiển điều hòa với tập phòng tương thích khác nhau:
        self.ac_1 = AirConditionerRemote("AC01", "Remote Daikin Tầng 1", "Kho B", compatible_rooms={"A101", "A102"})
        self.ac_2 = AirConditionerRemote("AC02", "Remote LG Tầng 2", "Kho B", compatible_rooms={"A203", "A204"})

        # - 3 micro có pin và tín hiệu khác nhau:
        # mic1: pin 20, sóng 80 (không sẵn sàng vì pin < 30)
        self.m_bad_pin = WirelessMicrophone("WM01", "Mic Shure A", "Kho C", battery_level=20, signal_quality=80)
        # mic2: pin 50, sóng 70 (sẵn sàng, điểm = 60.0)
        self.m_ok = WirelessMicrophone("WM02", "Mic Sennheiser B", "Kho C", battery_level=50, signal_quality=70)
        # mic3: pin 90, sóng 90 (sẵn sàng, điểm = 90.0)
        self.m_best = WirelessMicrophone("WM03", "Mic Sony C", "Kho C", battery_level=90, signal_quality=90)

    # 1. Thêm thiết bị vào repository
    def test_01_add_devices_to_repository(self):
        repo = InMemoryRepository[ProjectorRemote]()
        repo.add(self.p_low)
        repo.add(self.p_mid)
        repo.add(self.p_high)
        self.assertEqual(len(repo.get_all()), 3)

    # 2. Thử thêm hai thiết bị trùng mã
    def test_02_duplicate_id_raises_exception(self):
        repo = InMemoryRepository[ProjectorRemote]()
        repo.add(self.p_mid)
        duplicate = ProjectorRemote("PR02", "Remote Trùng", "Kho A", battery_level=80)
        with self.assertRaises(DuplicateIdException):
            repo.add(duplicate)

    # 3. Tìm thiết bị theo mã
    def test_03_find_by_id(self):
        repo = InMemoryRepository[ProjectorRemote]()
        repo.add(self.p_mid)
        found = repo.find_by_id("PR02")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Remote Epson (Trung bình)")

    # 4. Lọc các thiết bị sẵn sàng
    def test_04_filter_ready_devices(self):
        repo = InMemoryRepository[ProjectorRemote]()
        repo.add(self.p_low)   # pin 10 -> False
        repo.add(self.p_mid)   # pin 60 -> True
        repo.add(self.p_high)  # pin 95 -> True

        ready_devices = repo.find_all(lambda d: d.is_ready_for_use())
        self.assertEqual(len(ready_devices), 2)
        self.assertEqual({d.id for d in ready_devices}, {"PR02", "PR03"})

    # 5. Chọn điều khiển máy chiếu có điểm cao nhất
    def test_05_allocate_projector_highest_priority(self):
        repo = InMemoryRepository[ProjectorRemote]()
        repo.add(self.p_low)
        repo.add(self.p_mid)
        repo.add(self.p_high)

        strategy = HighestPriorityStrategy[ProjectorRemote](lambda d: d.get_default_priority_score())
        service = AllocationService[ProjectorRemote](repo, strategy)

        selected = service.allocate()
        self.assertEqual(selected.id, "PR03")
        self.assertEqual(selected.battery_level, 95)
        self.assertEqual(selected.status, DeviceStatus.BORROWED)

    # 6. Chọn điều khiển điều hòa tương thích với một phòng
    def test_06_allocate_air_conditioner_for_specific_room(self):
        repo = InMemoryRepository[AirConditionerRemote]()
        repo.add(self.ac_1)  # A101, A102
        repo.add(self.ac_2)  # A203, A204

        strategy = FirstAvailableStrategy[AirConditionerRemote]()
        service = AllocationService[AirConditionerRemote](repo, strategy)

        # Cấp phát cho phòng A203
        selected = service.allocate(additional_condition=lambda d: d.is_compatible_with("A203"))
        self.assertEqual(selected.id, "AC02")
        self.assertTrue(selected.is_compatible_with("A203"))

    # 7. Chọn micro đầu tiên sẵn sàng
    def test_07_allocate_first_available_microphone(self):
        repo = InMemoryRepository[WirelessMicrophone]()
        repo.add(self.m_bad_pin)  # Không sẵn sàng
        repo.add(self.m_ok)       # Sẵn sàng đầu tiên
        repo.add(self.m_best)     # Sẵn sàng tiếp theo

        strategy = FirstAvailableStrategy[WirelessMicrophone]()
        service = AllocationService[WirelessMicrophone](repo, strategy)

        selected = service.allocate()
        # WM01 bị bỏ qua vì is_ready_for_use() là False, nên WM02 được chọn đầu tiên
        self.assertEqual(selected.id, "WM02")

    # 8. Đổi chiến lược trong thời gian chạy và quan sát kết quả
    def test_08_change_strategy_at_runtime(self):
        repo = InMemoryRepository[WirelessMicrophone]()
        repo.add(self.m_ok)    # điểm 60
        repo.add(self.m_best)  # điểm 90

        # Ban đầu: FirstAvailableStrategy -> chọn m_ok
        service = AllocationService[WirelessMicrophone](repo, FirstAvailableStrategy[WirelessMicrophone]())
        # Giả lập chưa mượn để so sánh lựa chọn chiến lược
        strategy1 = service.strategy
        chosen1 = strategy1.select([self.m_ok, self.m_best])
        self.assertEqual(chosen1.id, "WM02")

        # Đổi sang: HighestPriorityStrategy -> chọn m_best
        service.change_strategy(HighestPriorityStrategy[WirelessMicrophone](lambda d: d.get_default_priority_score()))
        chosen2 = service.strategy.select([self.m_ok, self.m_best])
        self.assertEqual(chosen2.id, "WM03")

    # 9. Thử cấp phát khi không có ứng viên phù hợp
    def test_09_allocate_no_suitable_item(self):
        repo = InMemoryRepository[ProjectorRemote]()
        repo.add(self.p_low)  # pin 10, không sẵn sàng

        service = AllocationService[ProjectorRemote](repo, FirstAvailableStrategy[ProjectorRemote]())
        with self.assertRaises(NoSuitableItemException):
            service.allocate()

    # 10. Chứng minh thiết bị được chọn chuyển sang Borrowed
    def test_10_selected_device_status_changes_to_borrowed(self):
        repo = InMemoryRepository[ProjectorRemote]()
        repo.add(self.p_high)
        self.assertEqual(self.p_high.status, DeviceStatus.AVAILABLE)

        service = AllocationService[ProjectorRemote](repo, FirstAvailableStrategy[ProjectorRemote]())
        selected = service.allocate()

        self.assertEqual(selected.status, DeviceStatus.BORROWED)
        self.assertEqual(self.p_high.status, DeviceStatus.BORROWED)

    # 11. Chứng minh repository tổng quát có thể dùng cho ít nhất hai loại thiết bị mà không sao chép mã
    def test_11_generic_repository_reusability(self):
        repo_proj = InMemoryRepository[ProjectorRemote]()
        repo_ac = InMemoryRepository[AirConditionerRemote]()

        repo_proj.add(self.p_mid)
        repo_ac.add(self.ac_1)

        self.assertEqual(repo_proj.find_by_id("PR02").name, self.p_mid.name)
        self.assertEqual(repo_ac.find_by_id("AC01").name, self.ac_1.name)


if __name__ == "__main__":
    unittest.main()
