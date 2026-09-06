import os
import tkinter as tk
from tkinter import messagebox, filedialog
import pymem
import pymem.process
import shutil


# ==================== 自动路径查找 ====================
def find_game_process():
    """自动查找游戏进程"""
    process_names = [
        "InsaniquariumDeluxe.exe",
        "Insaniquarium.exe",
        "InsaniqariumDeluxe.exe"
    ]
    for name in process_names:
        try:
            pm = pymem.Pymem(name)
            pm.close_process()
            return name
        except:
            continue
    return None


def find_save_path():
    """自动查找存档路径（基于游戏进程位置）"""

    # 方法1：从游戏进程路径推断（最可靠）
    try:
        process_name = find_game_process()
        if process_name:
            pm = pymem.Pymem(process_name)
            # 获取进程的exe路径
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                if proc.info['name'].lower() == process_name.lower():
                    exe_dir = os.path.dirname(proc.info['exe'])
                    save_path = os.path.join(exe_dir, "userdata", "user1.dat")
                    if os.path.exists(save_path):
                        pm.close_process()
                        return save_path
            pm.close_process()
    except:
        pass

    # 方法2：常见安装目录（备选）
    common_paths = [
        "C:/Program Files (x86)/PopCap Games/Insaniquarium/userdata/user1.dat",
        "C:/Program Files/PopCap Games/Insaniquarium/userdata/user1.dat",
        os.path.expanduser("~/Documents/PopCap Games/Insaniquarium/userdata/user1.dat"),
        os.path.expanduser("~/AppData/Local/PopCap Games/Insaniquarium/userdata/user1.dat"),
        os.path.expanduser("~/AppData/Roaming/PopCap Games/Insaniquarium/userdata/user1.dat"),
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path

    # 方法3：当前目录的userdata（方便调试）
    local_path = os.path.join(os.path.dirname(__file__), "userdata", "user1.dat")
    if os.path.exists(local_path):
        return local_path

    return None


# ==================== 内存操作核心 ====================
class GameMemory:
    def __init__(self):
        self.pm = None
        self.money_addr = 0
        self.attached = False

    def attach(self):
        try:
            process_name = find_game_process()
            if not process_name:
                return False, "❌ 找不到游戏进程"

            self.pm = pymem.Pymem(process_name)
            self.attached = True

            module = pymem.process.module_from_name(self.pm.process_handle, process_name)
            base = module.lpBaseOfDll

            # 第一步：基址 + 0x18D630
            addr1 = base + 0x18D630
            print(f"📍 第1层地址: {hex(addr1)}")
            ptr1 = self.pm.read_int(addr1)
            print(f"   读到: {hex(ptr1)}")

            # 第二步：ptr1 + 0x620
            addr2 = ptr1 + 0x620
            print(f"📍 第2层地址: {hex(addr2)}")
            ptr2 = self.pm.read_int(addr2)
            print(f"   读到: {hex(ptr2)}")

            # 第三步：ptr2 + 0x3C0 = 金币地址
            self.money_addr = ptr2 + 0x3C0
            print(f"💰 金币地址: {hex(self.money_addr)}")

            return True, f"✅ 连接成功，金币地址: {hex(self.money_addr)}"

        except Exception as e:
            self.attached = False
            return False, f"❌ 连接失败: {e}"

    def read_money(self):
        if not self.attached or self.money_addr == 0:
            return 0
        try:
            return self.pm.read_int(self.money_addr)
        except:
            return None

    def write_money(self, value):
        if not self.attached or self.money_addr == 0:
            return False
        try:
            self.pm.write_int(self.money_addr, value)
            return True
        except:
            return False

    def detach(self):
        if self.pm:
            self.pm.close_process()
        self.pm = None
        self.attached = False
        self.money_addr = 0


# ==================== 存档操作核心 ====================
class SaveHacker:
    def __init__(self, path=None):
        if path is None:
            path = find_save_path()
        self.path = path
        self.data = None
        self.loaded = False

    def load(self):
        if not self.path or not os.path.exists(self.path):
            return False, f"❌ 找不到存档: {self.path if self.path else '请手动选择'}"
        try:
            with open(self.path, "rb") as f:
                self.data = bytearray(f.read())
            self.loaded = True
            return True, f"✅ 存档加载成功: {os.path.basename(self.path)}"
        except Exception as e:
            return False, f"❌ 加载失败: {e}"

    def save(self):
        if not self.loaded:
            return False
        with open(self.path, "wb") as f:
            f.write(self.data)
        return True

    def read_int(self, offset, size=4):
        return int.from_bytes(self.data[offset:offset + size], 'little')

    def write_int(self, offset, value, size=4):
        self.data[offset:offset + size] = value.to_bytes(size, 'little')

    def write_byte(self, offset, value):
        self.data[offset] = value & 0xFF

    def read_byte(self, offset):
        return self.data[offset]

    def write_flag_range(self, start, end, value=1):
        for i in range(start, end + 1):
            self.data[i] = value

    # ----- 快捷功能 -----
    def set_shells(self, val):
        self.write_int(0x00, val)

    def get_shells(self):
        return self.read_int(0x00)

    def set_level(self, big, small):
        self.write_int(0x08, big)
        self.write_int(0x0C, small)

    def get_level(self):
        big = self.read_int(0x08)
        small = self.read_int(0x0C)
        return big, small

    def set_loop(self, val):
        self.write_byte(0x22, val)

    def get_loop(self):
        return self.read_byte(0x22)

    def set_trophy(self):
        self.write_byte(0x33, 0x06)

    def get_trophy(self):
        return self.read_byte(0x33)

    def set_pet_limit(self, val):
        self.write_int(0x36, val, size=4)

    def get_pet_limit(self):
        return self.read_int(0x36, size=4)

    def unlock_eggs(self):
        self.write_flag_range(0x3A, 0x52)

    def unlock_bg(self):
        self.write_flag_range(0x53, 0x57)

    def unlock_challenge_btns(self):
        for off in [0x10, 0x11, 0x12]:
            self.write_byte(off, 1)

    def unlock_challenge_data(self):
        # 挑战关解锁标志偏移列表
        challenge_offsets = [0x60, 0x69, 0x72, 0x7B]

        for off in challenge_offsets:
            self.write_byte(off, 0x01)

    def unlock_all(self):
        self.set_shells(9999)
        self.set_level(100, 99)
        self.set_loop(255)
        self.set_trophy()
        self.set_pet_limit(10)
        self.unlock_eggs()
        self.unlock_bg()
        self.unlock_challenge_btns()
        self.unlock_challenge_data()
        return self.save()


# ==================== 主界面 ====================
class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("🐠 怪怪水族馆 修改器")
        self.root.geometry("450x450")
        self.root.resizable(False, False)

        self.mem = GameMemory()
        self.lock_active = False
        self.lock_thread = None
        self.save_hacker = None

        # 自动检测
        self.game_process = find_game_process()
        self.save_path = find_save_path()

        self.create_widgets()
        self.update_status("就绪", "gray")
        self.update_money_display()

    def create_widgets(self):
        tk.Label(self.root, text="🐠 怪怪水族馆 修改器", font=("Arial", 16, "bold")).pack(pady=10)

        # 状态
        self.status_label = tk.Label(self.root, text="状态: 未连接", font=("Arial", 10))
        self.status_label.pack()

        # 进程/存档状态
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)
        if self.game_process:
            tk.Label(info_frame, text=f"✅ 游戏: {self.game_process}", fg="green").pack()
        else:
            tk.Label(info_frame, text="❌ 未找到游戏进程", fg="red").pack()

        if self.save_path:
            tk.Label(info_frame, text=f"✅ 存档: {os.path.basename(self.save_path)}", fg="green").pack()
        else:
            tk.Label(info_frame, text="❌ 未找到存档", fg="red").pack()

        # 连接按钮
        self.connect_btn = tk.Button(self.root, text="🔗 连接游戏关卡", command=self.attach_game, width=20)
        self.connect_btn.pack(pady=5)

        # ====== 金币修改 ======
        frame_money = tk.LabelFrame(self.root, text="💰 金币修改", padx=10, pady=10)
        frame_money.pack(pady=10, fill="x", padx=20)

        self.money_label = tk.Label(frame_money, text="当前金币: 未知", font=("Arial", 12))
        self.money_label.pack()

        row = tk.Frame(frame_money)
        row.pack(pady=5)

        tk.Label(row, text="设置金币:").pack(side=tk.LEFT, padx=5)
        self.money_entry = tk.Entry(row, width=12)
        self.money_entry.insert(0, "99999")
        self.money_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(row, text="✅ 设置", command=self.set_money).pack(side=tk.LEFT, padx=2)
        tk.Button(row, text="🔄 刷新", command=self.refresh_money).pack(side=tk.LEFT, padx=2)
        self.lock_btn = tk.Button(row, text="🔒 锁定", command=self.toggle_lock, bg="lightgray", width=6)
        self.lock_btn.pack(side=tk.LEFT, padx=5)

        # ====== 底部 ======
        bottom = tk.Frame(self.root)
        bottom.pack(pady=15)

        tk.Button(bottom, text="📂 存档修改器", command=self.open_save_window, bg="lightblue", width=15).pack(
            side=tk.LEFT, padx=5)
        tk.Button(bottom, text="退出", command=self.root.quit, width=10).pack(side=tk.LEFT, padx=5)

    def update_status(self, text, color="black"):
        self.status_label.config(text=f"状态: {text}", fg=color)

    def attach_game(self):
        # 如果已经连接，先断开
        if self.mem.attached:
            self.mem.detach()
            self.connect_btn.config(text="🔗 刷新连接")
            self.update_status("已断开，正在重新连接...", "orange")

        success, msg = self.mem.attach()
        if success:
            self.update_status(msg, "green")
            self.refresh_money()
        else:
            self.update_status(msg, "red")

    def refresh_money(self):
        if not self.mem.attached:
            self.money_label.config(text="当前金币: 未连接")
            self.update_status("请先连接游戏", "red")
            return
        money = self.mem.read_money()
        if money is None:
            self.money_label.config(text="当前金币: 读取失败")
            self.update_status("读取失败，请检查游戏是否在关卡中", "red")
        else:
            self.money_label.config(text=f"当前金币: {money}")
            self.update_status(f"当前金币: {money}", "green")

    def set_money(self):
        if not self.mem.attached:
            self.update_status("请先连接游戏", "red")
            return
        try:
            val = int(self.money_entry.get())
            if self.mem.write_money(val):
                self.update_status(f"✅ 已设为 {val}", "green")
                self.refresh_money()
            else:
                self.update_status("❌ 写入失败", "red")
        except ValueError:
            self.update_status("❌ 请输入有效数字", "red")

    def toggle_lock(self):
        """切换金币锁定状态"""
        if not self.mem.attached:
            self.update_status("请先连接游戏", "red")
            return

        self.lock_active = not self.lock_active

        if self.lock_active:
            self.lock_btn.config(text="🔓 解锁", bg="lightcoral")
            self.update_status("🔒 金币已锁定（每0.2秒刷新）", "blue")
            # 启动后台线程
            import threading
            self.lock_thread = threading.Thread(target=self.lock_loop, daemon=True)
            self.lock_thread.start()
        else:
            self.lock_btn.config(text="🔒 锁定", bg="lightgray")
            self.update_status("🔓 已解锁", "green")

    def lock_loop(self):
        """后台锁定线程"""
        while self.lock_active:
            if self.mem.attached and self.mem.money_addr:
                try:
                    # 读取当前值，如果小于目标值就改
                    current = self.mem.read_money()
                    target = int(self.money_entry.get()) if self.money_entry.get().isdigit() else 99999
                    if current != target:
                        self.mem.write_money(target)
                except:
                    pass
            import time
            time.sleep(0.15)

    def update_money_display(self):
        """定时刷新金币显示"""
        if self.mem.attached:
            try:
                money = self.mem.read_money()
                if money is not None:
                    self.money_label.config(text=f"当前金币: {money}")
            except:
                pass
        self.root.after(3000, self.update_money_display)

    def open_save_window(self):
        if not self.save_path:
            messagebox.showerror("错误", "找不到存档文件")
            return
        SaveWindow(self.root, self.save_path)


# ==================== 存档修改窗口 ====================
class SaveWindow:
    def __init__(self, parent, save_path):
        self.window = tk.Toplevel(parent)
        self.window.title("📂 存档修改器")
        self.window.geometry("500x580")
        self.window.resizable(False, False)

        self.save_path = save_path
        self.save = SaveHacker(save_path)

        # 警告
        tk.Label(self.window, text="⚠️ 修改存档时请切换至其他用户或关闭游戏！", fg="red", font=("Arial", 12, "bold")).pack(pady=10)

        # 路径输入框
        frame_path = tk.Frame(self.window)
        frame_path.pack(pady=5, fill="x", padx=20)

        tk.Label(frame_path, text="存档路径:").pack(side=tk.LEFT)
        self.path_entry = tk.Entry(frame_path, width=35)
        self.path_entry.insert(0, save_path)
        self.path_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(frame_path, text="📂 浏览", command=self.browse_save).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_path, text="🔄 重载", command=self.reload_save).pack(side=tk.LEFT, padx=2)
        self.status = tk.Label(self.window, text="状态: 加载中...", fg="gray")
        self.status.pack(pady=5)

        self.create_controls()
        self.load_save()

    def browse_save(self):
        """浏览选择存档文件"""
        path = filedialog.askopenfilename(
            title="选择存档文件",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
        )
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.reload_save()

    def reload_save(self):
        """重新加载存档"""
        self.save_path = self.path_entry.get()
        self.save = SaveHacker(self.save_path)
        # 清空旧数据
        self.shells_entry.delete(0, tk.END)
        self.big_entry.delete(0, tk.END)
        self.small_entry.delete(0, tk.END)
        self.loop_entry.delete(0, tk.END)
        self.pet_limit_entry.delete(0, tk.END)
        self.load_save()

    def load_save(self):
        ok, msg = self.save.load()
        if ok:
            self.update_status(msg, "green")

            # 全部清空
            self.shells_entry.delete(0, tk.END)
            self.big_entry.delete(0, tk.END)
            self.small_entry.delete(0, tk.END)
            self.loop_entry.delete(0, tk.END)
            self.pet_limit_entry.delete(0, tk.END)

            # 插入新数据
            self.shells_entry.insert(0, str(self.save.get_shells()))
            big, small = self.save.get_level()
            self.big_entry.insert(0, str(big))
            self.small_entry.insert(0, str(small))
            self.loop_entry.insert(0, str(self.save.get_loop()))
            self.pet_limit_entry.insert(0, str(self.save.get_pet_limit()))

        else:
            self.update_status(msg, "red")

    def create_controls(self):
        frame = tk.LabelFrame(self.window, text="存档数据修改", padx=10, pady=10)
        frame.pack(pady=10, fill="x", padx=20)

        # 贝壳
        row1 = tk.Frame(frame)
        row1.pack(fill="x", pady=2)
        tk.Label(row1, text="贝壳:").pack(side=tk.LEFT)
        self.shells_entry = tk.Entry(row1, width=10)
        self.shells_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(row1, text="设置", command=self.set_shells).pack(side=tk.LEFT, padx=2)

        # 关卡
        row2 = tk.Frame(frame)
        row2.pack(fill="x", pady=2)
        tk.Label(row2, text="大关/小关:").pack(side=tk.LEFT)
        self.big_entry = tk.Entry(row2, width=5)
        self.big_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(row2, text="/").pack(side=tk.LEFT)
        self.small_entry = tk.Entry(row2, width=5)
        self.small_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(row2, text="设置", command=self.set_level).pack(side=tk.LEFT, padx=2)

        # 循环次数
        row3 = tk.Frame(frame)
        row3.pack(fill="x", pady=2)
        tk.Label(row3, text="循环次数:").pack(side=tk.LEFT)
        self.loop_entry = tk.Entry(row3, width=10)
        self.loop_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(row3, text="设置", command=self.set_loop).pack(side=tk.LEFT, padx=2)

        # 宠物上限
        row4 = tk.Frame(frame)
        row4.pack(fill="x", pady=2)
        tk.Label(row4, text="虚拟鱼缸宠物上限:").pack(side=tk.LEFT)
        self.pet_limit_entry = tk.Entry(row4, width=10)
        self.pet_limit_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(row4, text="设置", command=self.set_pet_limit).pack(side=tk.LEFT, padx=2)

        # 一键功能
        tk.Label(frame, text="--- 一键功能 ---", fg="blue").pack(pady=5)
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=2)
        tk.Button(btn_frame, text="🥚 解锁全部蛋", command=self.unlock_eggs, bg="lightblue").pack(side=tk.LEFT, padx=2,
                                                                                                 fill="x", expand=True)
        tk.Button(btn_frame, text="🏆 银奖杯", command=self.set_trophy, bg="gold").pack(side=tk.LEFT, padx=2, fill="x",
                                                                                       expand=True)

        btn_frame2 = tk.Frame(frame)
        btn_frame2.pack(fill="x", pady=2)
        tk.Button(btn_frame2, text="🖼️ 虚拟鱼缸背景解锁", command=self.unlock_bg, bg="lightgreen").pack(side=tk.LEFT, padx=2,
                                                                                                fill="x", expand=True)
        tk.Button(btn_frame2, text="🎯 挑战关一键解锁", command=self.unlock_challenge_btns, bg="lightcoral").pack(side=tk.LEFT,
                                                                                                           padx=2,
                                                                                                           fill="x",
                                                                                                           expand=True)

        # 全解锁
        tk.Button(frame, text="🌟 一键全解锁", command=self.unlock_all, bg="red", fg="white",
                  font=("Arial", 10, "bold")).pack(fill="x", pady=5)

        # 备份
        tk.Button(frame, text="💾 备份存档", command=self.backup_save, bg="lightgray").pack(fill="x", pady=2)

        # 关闭
        tk.Button(self.window, text="关闭", command=self.window.destroy).pack(pady=10)

    def update_status(self, text, color="black"):
        self.status.config(text=f"状态: {text}", fg=color)

    def save_and_reload(self):
        self.save.save()
        self.load_save()

    def set_shells(self):
        try:
            v = int(self.shells_entry.get())
            self.save.set_shells(v)
            self.save_and_reload()
            self.update_status(f"✅ 贝壳已设为 {v}", "green")
        except Exception as e:
            self.update_status(f"❌ 设置失败: {e}", "red")

    def set_level(self):
        try:
            b = int(self.big_entry.get())
            s = int(self.small_entry.get())
            self.save.set_level(b, s)
            self.save_and_reload()
            self.update_status(f"✅ 关卡已设为 {b}-{s}", "green")
        except Exception as e:
            self.update_status(f"❌ 设置失败: {e}", "red")

    def set_loop(self):
        try:
            v = int(self.loop_entry.get())
            self.save.set_loop(v)
            self.save_and_reload()
            self.update_status(f"✅ 循环次数已设为 {v}", "green")
        except Exception as e:
            self.update_status(f"❌ 设置失败: {e}", "red")

    def set_pet_limit(self):
        try:
            v = int(self.pet_limit_entry.get())
            self.save.set_pet_limit(v)
            self.save_and_reload()
            self.update_status(f"✅ 宠物上限已设为 {v}", "green")
        except Exception as e:
            self.update_status(f"❌ 设置失败: {e}", "red")

    def unlock_eggs(self):
        self.save.unlock_eggs()
        self.save_and_reload()
        self.update_status("✅ 已解锁全部蛋/宠物", "green")

    def set_trophy(self):
        self.save.set_trophy()
        self.save_and_reload()
        self.update_status("✅ 已获得银奖杯", "green")

    def unlock_bg(self):
        self.save.unlock_bg()
        self.save_and_reload()
        self.update_status("✅ 已解锁虚拟鱼缸背景", "green")

    def unlock_challenge_btns(self):
        self.save.unlock_challenge_btns()
        self.save_and_reload()
        self.update_status("✅ 已解锁挑战按钮", "green")

    def unlock_all(self):
        if self.save.unlock_all():
            self.load_save()
            self.update_status("🌟 全解锁完成！", "red")
            messagebox.showinfo("成功", "🌟 全解锁完成！\n所有宠物、背景、奖杯、关卡已解锁。")
        else:
            self.update_status("❌ 保存失败", "red")

    def backup_save(self):
        try:
            backup = self.save_path + ".backup"
            shutil.copy2(self.save_path, backup)
            self.update_status(f"✅ 已备份到: {os.path.basename(backup)}", "green")
        except Exception as e:
            self.update_status(f"❌ 备份失败: {e}", "red")


# ==================== 启动 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()