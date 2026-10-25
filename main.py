from __future__ import annotations
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


from models.device_status import DeviceStatus
from models.projector_remote import ProjectorRemote
from models.air_conditioner_remote import AirConditionerRemote
from models.wireless_microphone import WirelessMicrophone
from repositories.in_memory_repository import InMemoryRepository
from strategies.highest_priority_strategy import HighestPriorityStrategy
from strategies.first_available_strategy import FirstAvailableStrategy
from services.allocation_service import AllocationService
from exceptions.device_exceptions import (
    DuplicateIdException,
    NoSuitableItemException,
    DeviceNotReadyException,
    DeviceOperationException,
)


def print_section(title: str) -> None:
    print("\n")
    print(f" {title}")


def print_step(step_no: int, description: str) -> None:
    print(f"\n{step_no}. {description}")


def main() -> None:
    print_section("HỆ THỐNG QUẢN LÝ THIẾT BỊ GIẢNG DẠY - DEMO KIỂM THỬ")

    # KHỞI TẠO DỮ LIỆU BAN ĐẦU
    print("\n>>> Khởi tạo dữ liệu mẫu:")
    # 3 Điều khiển máy chiếu với mức pin khác nhau
    p_low = ProjectorRemote("PR01", "Remote Sony Phòng Lab", "Kho A - Kệ 1", battery_level=15)
    p_mid = ProjectorRemote("PR02", "Remote Epson Hội trường", "Kho A - Kệ 2", battery_level=60)
    p_high = ProjectorRemote("PR03", "Remote Panasonic Giảng đường", "Kho A - Kệ 3", battery_level=95)

    # 2 Điều khiển điều hòa với tập phòng tương thích khác nhau
    ac_t1 = AirConditionerRemote("AC01", "Remote Daikin Tầng 1", "Kho B - Hộc 1", compatible_rooms={"A101", "A102", "A103"})
    ac_t2 = AirConditionerRemote("AC02", "Remote LG Tầng 2", "Kho B - Hộc 2", compatible_rooms={"A203", "A204"})

    # 3 Micro không dây với pin và chất lượng tín hiệu khác nhau
    m_low_pin = WirelessMicrophone("WM01", "Mic Shure A (Pin yếu)", "Kho C", battery_level=20, signal_quality=85)
    m_ready_std = WirelessMicrophone("WM02", "Mic Sennheiser B (Chuẩn)", "Kho C", battery_level=50, signal_quality=70)
    m_ready_vip = WirelessMicrophone("WM03", "Mic Sony C (Chất lượng cao)", "Kho C", battery_level=90, signal_quality=95)

    print(" - Điều khiển máy chiếu: PR01 (15% pin), PR02 (60% pin), PR03 (95% pin)")
    print(" - Điều khiển điều hòa : AC01 (Phòng A101, A102, A103), AC02 (Phòng A203, A204)")
    print(" - Micro không dây     : WM01 (20% pin, 85% sóng), WM02 (50% pin, 70% sóng), WM03 (90% pin, 95% sóng)")

    # 1. Thêm thiết bị vào repository
    print_step(1, "Thêm thiết bị vào Generic InMemoryRepository")
    proj_repo = InMemoryRepository[ProjectorRemote]()
    proj_repo.add(p_low)
    proj_repo.add(p_mid)
    proj_repo.add(p_high)
    print(f"-> Đã thêm thành công {len(proj_repo.get_all())} điều khiển máy chiếu vào repo.")
    for d in proj_repo.get_all():
        print(f"   + [{d.id}] {d.name} | Pin: {d.battery_level}% | Trạng thái: {d.status} | Sẵn sàng: {d.is_ready_for_use()}")

    # 2. Thử thêm hai thiết bị trùng mã
    print_step(2, "Thử thêm hai thiết bị trùng mã định danh (Id)")
    try:
        dup_projector = ProjectorRemote("PR01", "Remote Trùng Lặp", "Kho A", battery_level=80)
        print("   Đang thử thêm thiết bị có id 'PR01' đã tồn tại...")
        proj_repo.add(dup_projector)
    except DuplicateIdException as e:
        print(f"-> [BẮT ĐƯỢC NGOẠI LỆ THÀNH CÔNG] DuplicateIdException: {e}")

    # 3. Tìm thiết bị theo mã
    print_step(3, "Tìm kiếm thiết bị theo mã (FindById)")
    search_id = "PR02"
    found = proj_repo.find_by_id(search_id)
    if found:
        print(f"-> Tìm thấy thiết bị '{search_id}': {found.name} (Vị trí: {found.storage_location})")
    else:
        print(f"-> Không tìm thấy thiết bị '{search_id}'")

    not_found = proj_repo.find_by_id("PR_KHONG_TON_TAI")
    print(f"-> Tra cứu mã không tồn tại 'PR_KHONG_TON_TAI': {not_found}")

    # 4. Lọc các thiết bị sẵn sàng
    print_step(4, "Lọc các thiết bị sẵn sàng (IsReadyForUse)")
    ready_projectors = proj_repo.find_all(lambda d: d.is_ready_for_use())
    print(f"-> Số thiết bị máy chiếu sẵn sàng (pin >= 20% và Available): {len(ready_projectors)}")
    for d in ready_projectors:
        print(f"   + [{d.id}] {d.name} | Pin: {d.battery_level}% | Điểm ưu tiên: {d.get_default_priority_score()}")

    # 5. Chọn điều khiển máy chiếu có điểm cao nhất
    print_step(5, "Chọn điều khiển máy chiếu có điểm cao nhất (HighestPriorityStrategy)")
    highest_strategy = HighestPriorityStrategy[ProjectorRemote](lambda d: d.get_default_priority_score())
    proj_service = AllocationService[ProjectorRemote](proj_repo, highest_strategy)

    allocated_projector = proj_service.allocate()
    print(f"-> Đã cấp phát thành công: [{allocated_projector.id}] {allocated_projector.name}")
    print(f"   + Mức pin: {allocated_projector.battery_level}% | Điểm: {allocated_projector.get_default_priority_score()}")
    print(f"   + Trạng thái sau cấp phát: {allocated_projector.status}")

    # 6. Chọn điều khiển điều hòa tương thích với một phòng
    print_step(6, "Chọn điều khiển điều hòa tương thích với một phòng (ví dụ: 'A203')")
    ac_repo = InMemoryRepository[AirConditionerRemote]()
    ac_repo.add(ac_t1)
    ac_repo.add(ac_t2)

    ac_service = AllocationService[AirConditionerRemote](ac_repo, FirstAvailableStrategy[AirConditionerRemote]())
    target_room = "A203"
    print(f"   Yêu cầu cấp phát điều khiển điều hòa cho phòng '{target_room}'...")
    allocated_ac = ac_service.allocate(additional_condition=lambda ac: ac.is_compatible_with(target_room))
    print(f"-> Đã cấp phát thành công: [{allocated_ac.id}] {allocated_ac.name}")
    print(f"   + Danh sách phòng hỗ trợ: {list(allocated_ac.compatible_rooms)}")
    print(f"   + Trạng thái sau cấp phát: {allocated_ac.status}")

    # 7. Chọn micro đầu tiên sẵn sàng
    print_step(7, "Chọn micro đầu tiên sẵn sàng (FirstAvailableStrategy)")
    mic_repo = InMemoryRepository[WirelessMicrophone]()
    mic_repo.add(m_low_pin)
    mic_repo.add(m_ready_std)
    mic_repo.add(m_ready_vip)

    mic_service = AllocationService[WirelessMicrophone](mic_repo, FirstAvailableStrategy[WirelessMicrophone]())
    allocated_mic = mic_service.allocate()
    print(f"-> Micro đầu tiên sẵn sàng được cấp phát: [{allocated_mic.id}] {allocated_mic.name}")
    print(f"   + Pin: {allocated_mic.battery_level}%, Sóng: {allocated_mic.signal_quality}% (Điểm TB: {allocated_mic.get_default_priority_score()})")
    print(f"   + (Lưu ý: WM01 bị bỏ qua do pin < 30% không sẵn sàng)")

    # 8. Đổi chiến lược trong thời gian chạy và quan sát kết quả
    print_step(8, "Đổi chiến lược trong thời gian chạy (ChangeStrategy)")
    # Giả lập trả lại micro để thử nghiệm việc lựa chọn giữa WM02 (chuẩn) và WM03 (vip)
    allocated_mic.return_device()
    print(f"   Khởi tạo lại: cả WM02 (điểm 60.0) và WM03 (điểm 92.5) đều sẵn sàng.")

    # Chiến lược 1: FirstAvailableStrategy
    mic_service.change_strategy(FirstAvailableStrategy[WirelessMicrophone]())
    print(f"   Chiến lược hiện tại: {mic_service.strategy}")
    choice1 = mic_service.strategy.select([m_ready_std, m_ready_vip])
    print(f"   -> Kết quả lựa chọn theo FirstAvailable: [{choice1.id}] {choice1.name}")

    # Đổi sang Chiến lược 2: HighestPriorityStrategy
    new_strategy = HighestPriorityStrategy[WirelessMicrophone](lambda m: m.get_default_priority_score())
    mic_service.change_strategy(new_strategy)
    print(f"   Chiến lược sau khi đổi: {mic_service.strategy}")
    choice2 = mic_service.strategy.select([m_ready_std, m_ready_vip])
    print(f"   -> Kết quả lựa chọn theo HighestPriority: [{choice2.id}] {choice2.name} (Điểm: {choice2.get_default_priority_score()})")

    # 9. Thử cấp phát khi không có ứng viên phù hợp
    print_step(9, "Thử cấp phát khi không có ứng viên phù hợp")
    empty_repo = InMemoryRepository[ProjectorRemote]()
    # Chỉ thêm máy chiếu hết pin
    empty_repo.add(ProjectorRemote("PR_DEAD", "Remote Hỏng", "Kho", battery_level=5))
    failing_service = AllocationService[ProjectorRemote](empty_repo, FirstAvailableStrategy[ProjectorRemote]())
    try:
        print("   Đang yêu cầu cấp phát từ kho không có thiết bị sẵn sàng...")
        failing_service.allocate()
    except NoSuitableItemException as e:
        print(f"-> [BẮT ĐƯỢC NGOẠI LỆ THÀNH CÔNG] NoSuitableItemException: {e}")

    # 10. Chứng minh thiết bị được chọn chuyển sang Borrowed và thao tác Trả
    print_step(10, "Chứng minh thiết bị chuyển sang Borrowed và hoàn trả thiết bị")
    demo_device = ProjectorRemote("PR99", "Remote Demo Borrow", "Kho A", battery_level=80)
    demo_repo = InMemoryRepository[ProjectorRemote]()
    demo_repo.add(demo_device)

    demo_service = AllocationService[ProjectorRemote](demo_repo, FirstAvailableStrategy[ProjectorRemote]())
    print(f"   Trạng thái ban đầu: {demo_device.status}")
    allocated = demo_service.allocate()
    print(f"   Trạng thái sau khi allocate(): {allocated.status} (Khẳng định: Chuyển sang BORROWED)")

    print("   Thử mượn lại lần nữa khi đang mượn:")
    try:
        allocated.borrow()
    except DeviceNotReadyException as e:
        print(f"   -> [BẮT NGOẠI LỆ THÀNH CÔNG] DeviceNotReadyException: {e}")

    print("   Thực hiện trả thiết bị về kho:")
    allocated.return_device()
    print(f"   -> Trạng thái sau khi return_device(): {allocated.status} (Khẳng định: Trở về AVAILABLE)")

    # 11. Chứng minh Repository và Service tổng quát dùng cho nhiều loại không sửa mã
    print_step(11, "Chứng minh tính tái sử dụng cao của Generic Repository & AllocationService")
    print("-> Đã sử dụng InMemoryRepository<T> đồng thời cho:")
    print(f"   1. ProjectorRemote (kho chứa {len(proj_repo.get_all())} máy chiếu)")
    print(f"   2. AirConditionerRemote (kho chứa {len(ac_repo.get_all())} điều hòa)")
    print(f"   3. WirelessMicrophone (kho chứa {len(mic_repo.get_all())} micro)")
    print("-> AllocationService<T> hoạt động hoàn toàn dựa trên abstract interface,")
    print("   không có bất kỳ câu lệnh 'if isinstance(device, ProjectorRemote)' nào.")
    print("   => Tuân thủ triệt để nguyên tắc Đa hình và Đóng/Mở (Open/Closed Principle)!")



if __name__ == "__main__":
    main()
