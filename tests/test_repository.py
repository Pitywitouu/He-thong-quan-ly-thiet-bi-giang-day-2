import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.projector_remote import ProjectorRemote
from models.wireless_microphone import WirelessMicrophone
from repositories.in_memory_repository import InMemoryRepository
from exceptions.device_exceptions import DuplicateIdException


class TestRepository(unittest.TestCase):
    def test_add_and_find_by_id(self):
        repo = InMemoryRepository[ProjectorRemote]()
        p1 = ProjectorRemote("PR01", "Remote A", "Kho 1", battery_level=80)
        repo.add(p1)

        found = repo.find_by_id("PR01")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Remote A")

        # Tìm mã không tồn tại trả về None
        self.assertIsNone(repo.find_by_id("NON_EXIST"))

    def test_duplicate_id_exception(self):
        repo = InMemoryRepository[ProjectorRemote]()
        p1 = ProjectorRemote("PR01", "Remote 1", "Kho 1", battery_level=80)
        p2 = ProjectorRemote("PR01", "Remote 2 (Trùng mã)", "Kho 2", battery_level=90)

        repo.add(p1)
        with self.assertRaises(DuplicateIdException) as ctx:
            repo.add(p2)
        self.assertEqual(ctx.exception.duplicate_id, "PR01")

    def test_remove(self):
        repo = InMemoryRepository[ProjectorRemote]()
        p1 = ProjectorRemote("PR01", "Remote 1", "Kho 1", battery_level=80)
        repo.add(p1)

        self.assertTrue(repo.remove("PR01"))
        self.assertIsNone(repo.find_by_id("PR01"))
        self.assertFalse(repo.remove("PR01"))  # Xóa lần 2 trả về False

    def test_get_all_immutability(self):
        repo = InMemoryRepository[ProjectorRemote]()
        p1 = ProjectorRemote("PR01", "Remote 1", "Kho 1", battery_level=80)
        repo.add(p1)

        all_items = repo.get_all()
        self.assertEqual(len(all_items), 1)

        # Sửa đổi danh sách trả về không được ảnh hưởng đến nội bộ kho
        all_items.clear()
        self.assertEqual(len(repo.get_all()), 1)

    def test_find_all_predicate(self):
        repo = InMemoryRepository[ProjectorRemote]()
        p1 = ProjectorRemote("PR01", "Remote 1", "Kho 1", battery_level=10)
        p2 = ProjectorRemote("PR02", "Remote 2", "Kho 1", battery_level=50)
        p3 = ProjectorRemote("PR03", "Remote 3", "Kho 1", battery_level=90)
        repo.add(p1)
        repo.add(p2)
        repo.add(p3)

        ready_items = repo.find_all(lambda device: device.is_ready_for_use())
        self.assertEqual(len(ready_items), 2)
        self.assertEqual([d.id for d in ready_items], ["PR02", "PR03"])

    def test_generic_usage_across_multiple_types(self):
        repo_projector = InMemoryRepository[ProjectorRemote]()
        repo_mic = InMemoryRepository[WirelessMicrophone]()

        repo_projector.add(ProjectorRemote("P01", "Projector Remote", "A1", battery_level=80))
        repo_mic.add(WirelessMicrophone("M01", "Mic Shure", "B1", battery_level=70, signal_quality=85))

        self.assertEqual(repo_projector.find_by_id("P01").name, "Projector Remote")
        self.assertEqual(repo_mic.find_by_id("M01").name, "Mic Shure")


if __name__ == "__main__":
    unittest.main()
