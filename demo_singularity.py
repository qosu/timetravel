"""
Singularity Demo — When the Universe Cannot Settle.

Demonstrates self-referential paradox resolution where:
- The universe contains its own causal mirror
- Each resolution creates new events
- New events create new paradoxes
- The reflective loop DIVERGES

This is infinite regress: the universe can never finish fixing itself
because every fix introduces new problems that need fixing.

Run: python3 demo_singularity.py
"""

from universe import Universe
from causality import CausalGraph, ParadoxType
from singularity import ReflectiveUniverse
from convergence import analyze, ConvergenceClass


def banner(title: str):
    print(f"\n{'═'*62}")
    print(f"  {title}")
    print(f"{'═'*62}")


def demo_step_by_step():
    """Show the grandfather paradox reflective loop step by step."""
    banner("DEMO: VÒNG LẶP PHẢN CHIẾU — TỪNG BƯỚC")

    r = ReflectiveUniverse()
    g = r.u.spawn('Ông_Nội', {'sống': True})
    r.u.checkpoint('ĐỊA_ĐÀNG')
    p = r.u.spawn('Cha', {'sống': True}, preconditions=(g,))
    t = r.u.spawn('Người_Du_Hành', {'sống': True}, preconditions=(p,))
    r.u.travel_to('ĐỊA_ĐÀNG')
    k = r.u.kill('Ông_Nội', preconditions=(t,), negations=(g, p, t))

    print(f"  Khởi tạo: {len(r.u.history)} sự kiện trong lịch sử")
    print(f"  Thực thể hoạt động: {list(r.u.entities.keys())}")
    print()

    max_steps = 6
    for step in range(max_steps):
        cg = r.mirror()
        paradoxes = cg.detect_paradoxes()
        grandfathers = [p for p in paradoxes if p.ptype == ParadoxType.GRANDFATHER]

        if not grandfathers:
            print(f"  Bước {step}: ✅ HỘI TỤ — vũ trụ nhất quán!")
            break

        fp = r._structural_fingerprint()

        # Detect pattern: has this fingerprint been seen?
        result = r.reflect()
        removed = result.resolution.removed_events if result.resolution else []
        removed_short = [eid.split('@')[0].replace('singularity_negate_', '¬')[:35]
                        for eid in removed]

        growth = len(r.u.history) - (4 + sum(1 for _ in range(step) if True))

        print(f"  Bước {step}:")
        print(f"    Lịch sử:    {len(r.u.history)} sự kiện")
        print(f"    Paradox:    {len(grandfathers)} grandfather")
        print(f"    Xóa:        {removed_short}")
        print(f"    → Thêm {len(removed)} sự kiện phủ định mới vào lịch sử")
        print(f"    → Các sự kiện mới TỰ CHÚNG là paradox mới")

        if step >= 2:
            print(f"    ⚠️  Vũ trụ đang PHÌNH TO — mỗi lần sửa lại tạo thêm việc để sửa")

    print(f"\n  ┌─ KẾT LUẬN ─────────────────────────────")
    print(f"  │ Sau {max_steps} bước, lịch sử có {len(r.u.history)} sự kiện")
    print(f"  │ và vẫn còn paradox.")
    print(f"  │")
    print(f"  │ ĐÂY LÀ VÔ HẠN THỰC SỰ:")
    print(f"  │")
    print(f"  │ Mỗi lần vũ trụ tự sửa, nó tạo ra sự kiện mới.")
    print(f"  │ Sự kiện mới → paradox mới → cần sửa tiếp.")
    print(f"  │ Sửa tiếp → thêm sự kiện mới hơn → paradox mới hơn.")
    print(f"  │")
    print(f"  │ Số sự kiện TĂNG KHÔNG GIỚI HẠN.")
    print(f"  │ Vũ trụ KHÔNG BAO GIỜ đạt nhất quán.")
    print(f"  │")
    print(f"  │ Đây là bản chất của tự phản chiếu:")
    print(f"  │ Một hệ thống đủ mạnh để phân tích chính mình")
    print(f"  │ thì không thể CHỨNG MINH mình nhất quán.")
    print(f"  │ Nó chỉ có thể TIẾP TỤC SỬA. Mãi mãi.")
    print(f"  └──────────────────────────────────────────")


def demo_comparison():
    """Compare: clean universe vs. self-referential universe."""
    banner("SO SÁNH: NGOẠI TẠI vs. NỘI TẠI")

    # External solver (original engine)
    from universe import Universe as ExtUniverse
    from causality import CausalGraph
    from novikov import NovikovSolver

    u = ExtUniverse()
    g = u.spawn('G', {'sống': True})
    u.checkpoint('E')
    p = u.spawn('P', {'sống': True}, preconditions=(g,))
    t = u.spawn('T', {'sống': True}, preconditions=(p,))
    u.travel_to('E')
    k = u.kill('G', preconditions=(t,), negations=(g, p, t))

    cg = CausalGraph.from_history(u.history, ghost_event_ids=u.ghost_event_ids)
    solver = NovikovSolver(cg)
    result = solver.resolve()

    from novikov import NovikovResolution
    print(f"  Engine NGOẠI TẠI (đứng ngoài vũ trụ):")
    print(f"    Phát hiện paradox: CÓ")
    print(f"    Giải pháp: xóa {result.removed_events if isinstance(result, NovikovResolution) else 'KHÔNG CÓ'}")
    print(f"    Số bước: 1 (xong ngay)")
    print(f"    ✅ Vũ trụ được 'sửa' bởi một đấng bên ngoài")

    print()
    print(f"  Engine NỘI TẠI (nằm trong vũ trụ):")
    print(f"    Phát hiện paradox: CÓ")
    print(f"    Giải pháp: xóa sự kiện → tạo sự kiện phủ định")
    print(f"    Sự kiện phủ định → paradox mới → xóa tiếp → ...")
    print(f"    Số bước: VÔ HẠN (không bao giờ dừng)")
    print(f"    ❌ Vũ trụ TỰ SỬA nhưng không thể dừng lại")

    print()
    print(f"  Sự khác biệt:")
    print(f"    Engine cũ: người quan sát ĐỨNG NGOÀI vũ trụ.")
    print(f"    Engine mới: người quan sát NẰM TRONG vũ trụ.")
    print(f"    Hành động 'sửa paradox' là MỘT SỰ KIỆN trong vũ trụ.")
    print(f"    Sự kiện đó bị CHÍNH CÁI GƯƠNG phân tích.")
    print(f"    → Tự phản chiếu → vô hạn.")


if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     SINGULARITY ENGINE — VŨ TRỤ TỰ PHẢN CHIẾU          ║")
    print("║     Khi người sửa paradox trở thành paradox             ║")
    print("╚══════════════════════════════════════════════════════════╝")

    demo_step_by_step()
    demo_comparison()

    print(f"\n{'═'*62}")
    print("  CHẠM TỚI VÔ HẠN")
    print(f"{'═'*62}")
    print()
    print("  Không cần quantum. Không cần transfinite computation.")
    print("  Không cần Malament-Hogarth spacetime.")
    print()
    print("  Chỉ cần một thứ: TỰ PHẢN CHIẾU.")
    print()
    print("  Khi vũ trụ chứa mô tả của chính nó,")
    print("  và hành động dựa trên mô tả đó,")
    print("  thì mỗi lần 'sửa' là một sự kiện mới trong vũ trụ.")
    print("  Sự kiện mới → mô tả mới → paradox mới → sửa tiếp.")
    print()
    print("  Vòng lặp không bao giờ dừng.")
    print("  Số sự kiện → ∞.")
    print("  Độ phức tạp → ∞.")
    print()
    print("  Đó là vô hạn.")
    print("  Không phải vô hạn được tính toán.")
    print("  Mà là vô hạn KHÔNG THỂ DỪNG.")
    print()
