import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# --- CÁC HÀM XỬ LÝ DATABASE ---

def load_data():
    """Tải dữ liệu từ database lên bảng"""
    for row in tree.get_children():
        tree.delete(row)
    
    conn = sqlite3.connect('nhansu.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM NhanSu")
    rows = cursor.fetchall()
    
    for row in rows:
        tree.insert("", tk.END, values=row)
    conn.close()

def clear_entries():
    """Xóa trắng các ô nhập liệu"""
    txt_cccd.delete(0, tk.END)
    txt_hoten.delete(0, tk.END)
    txt_ngaysinh.delete(0, tk.END)
    cbo_gioitinh.set('')
    txt_diachi.delete(0, tk.END)

def add_data():
    """Chức năng THÊM MỚI"""
    cccd = txt_cccd.get()
    hoten = txt_hoten.get()
    ngaysinh = txt_ngaysinh.get()
    gioitinh = cbo_gioitinh.get()
    diachi = txt_diachi.get()

    if cccd == "" or hoten == "":
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập ít nhất Số CCCD và Họ tên!")
        return

    try:
        conn = sqlite3.connect('nhansu.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO NhanSu VALUES (?, ?, ?, ?, ?)", (cccd, hoten, ngaysinh, gioitinh, diachi))
        conn.commit()
        conn.close()
        
        clear_entries()
        load_data()
        messagebox.showinfo("Thành công", "Đã thêm nhân sự mới!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Lỗi", "Số CCCD này đã tồn tại trong hệ thống!")

def update_data():
    """Chức năng SỬA"""
    cccd = txt_cccd.get()
    hoten = txt_hoten.get()
    ngaysinh = txt_ngaysinh.get()
    gioitinh = cbo_gioitinh.get()
    diachi = txt_diachi.get()

    if cccd == "":
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn hoặc nhập Số CCCD cần sửa!")
        return

    conn = sqlite3.connect('nhansu.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE NhanSu 
        SET HoTen=?, NgaySinh=?, GioiTinh=?, DiaChi=? 
        WHERE SoCCCD=?
    """, (hoten, ngaysinh, gioitinh, diachi, cccd))
    conn.commit()
    conn.close()

    clear_entries()
    load_data()
    messagebox.showinfo("Thành công", "Đã cập nhật thông tin nhân sự!")

def delete_data():
    """Chức năng XÓA"""
    cccd = txt_cccd.get()
    
    if cccd == "":
        messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân sự cần xóa!")
        return

    # Hỏi lại để xác nhận
    confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa nhân sự có CCCD {cccd} không?")
    if confirm:
        conn = sqlite3.connect('nhansu.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM NhanSu WHERE SoCCCD=?", (cccd,))
        conn.commit()
        conn.close()

        clear_entries()
        load_data()
        messagebox.showinfo("Thành công", "Đã xóa nhân sự!")

def on_tree_select(event):
    """Bấm vào 1 dòng trong bảng thì tự động điền dữ liệu lên các ô nhập"""
    selected_item = tree.focus()
    if selected_item:
        values = tree.item(selected_item, 'values')
        clear_entries()
        txt_cccd.insert(0, values[0])
        txt_hoten.insert(0, values[1])
        txt_ngaysinh.insert(0, values[2])
        cbo_gioitinh.set(values[3])
        txt_diachi.insert(0, values[4])

# --- KHỞI TẠO GIAO DIỆN CHÍNH ---
root = tk.Tk()
root.title("Phần mềm Quản lý Nhân sự")
root.geometry("800x500")

# --- KHU VỰC 1: CÁC Ô NHẬP LIỆU ---
frame_nhaplieu = tk.Frame(root)
frame_nhaplieu.pack(pady=10)

tk.Label(frame_nhaplieu, text="Số CCCD:").grid(row=0, column=0, padx=5, pady=5)
txt_cccd = tk.Entry(frame_nhaplieu)
txt_cccd.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_nhaplieu, text="Họ tên:").grid(row=0, column=2, padx=5, pady=5)
txt_hoten = tk.Entry(frame_nhaplieu)
txt_hoten.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_nhaplieu, text="Ngày sinh:").grid(row=1, column=0, padx=5, pady=5)
txt_ngaysinh = tk.Entry(frame_nhaplieu)
txt_ngaysinh.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_nhaplieu, text="Giới tính:").grid(row=1, column=2, padx=5, pady=5)
cbo_gioitinh = ttk.Combobox(frame_nhaplieu, values=["Nam", "Nữ"])
cbo_gioitinh.grid(row=1, column=3, padx=5, pady=5)

tk.Label(frame_nhaplieu, text="Địa chỉ:").grid(row=2, column=0, padx=5, pady=5)
txt_diachi = tk.Entry(frame_nhaplieu, width=43)
txt_diachi.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

# --- KHU VỰC 2: CÁC NÚT BẤM (Đã gán lệnh) ---
frame_nutbam = tk.Frame(root)
frame_nutbam.pack(pady=10)

# Gán command cho các nút
tk.Button(frame_nutbam, text="Thêm Mới", width=10, command=add_data).grid(row=0, column=0, padx=10)
tk.Button(frame_nutbam, text="Sửa", width=10, command=update_data).grid(row=0, column=1, padx=10)
tk.Button(frame_nutbam, text="Xóa", width=10, command=delete_data).grid(row=0, column=2, padx=10)
tk.Button(frame_nutbam, text="Làm Mới", width=10, command=lambda:[clear_entries(), load_data()]).grid(row=0, column=3, padx=10)

# --- KHU VỰC 3: BẢNG HIỂN THỊ DỮ LIỆU ---
columns = ("SoCCCD", "HoTen", "NgaySinh", "GioiTinh", "DiaChi")
tree = ttk.Treeview(root, columns=columns, show="headings")

tree.heading("SoCCCD", text="Số CCCD")
tree.heading("HoTen", text="Họ và tên")
tree.heading("NgaySinh", text="Ngày sinh")
tree.heading("GioiTinh", text="Giới tính")
tree.heading("DiaChi", text="Địa chỉ thường trú")

tree.column("SoCCCD", width=100)
tree.column("HoTen", width=150)
tree.column("NgaySinh", width=100)
tree.column("GioiTinh", width=80)
tree.column("DiaChi", width=250)

tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# Gán sự kiện click chuột vào bảng
tree.bind("<ButtonRelease-1>", on_tree_select)

# Khởi động app
load_data()
root.mainloop()