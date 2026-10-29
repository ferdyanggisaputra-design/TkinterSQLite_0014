import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB = "prediksi_diabetes.db"


class Aplikasi:
    def __init__(self, root):
        self.root = root
        root.title("Prediksi Risiko Diabetes")
        root.geometry("620x500")

        self.conn = sqlite3.connect(DB)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS pasien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_pasien TEXT NOT NULL,
                usia INTEGER NOT NULL,
                gula_darah REAL NOT NULL,
                bmi REAL NOT NULL,
                riwayat_ortu TEXT NOT NULL,
                hasil_prediksi TEXT NOT NULL
            )
        """)
        self.conn.commit()

        self.nama = tk.StringVar()
        self.usia = tk.StringVar()
        self.gula = tk.StringVar()
        self.bmi = tk.StringVar()
        self.riwayat = tk.StringVar(value="Tidak")

        self.buat_form()
        root.protocol("WM_DELETE_WINDOW", self.tutup)

    def buat_form(self):
        frame = ttk.Frame(self.root, padding=25)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(
            frame,
            text="Prediksi Risiko Diabetes",
            font=("Arial", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        data_form = [
            ("Nama pasien", self.nama),
            ("Usia", self.usia),
            ("Gula darah (mg/dL)", self.gula),
            ("BMI", self.bmi)
        ]

        for baris, (teks, variabel) in enumerate(data_form, start=1):
            ttk.Label(frame, text=teks).grid(
                row=baris, column=0, sticky="w", pady=7
            )
            ttk.Entry(frame, textvariable=variabel).grid(
                row=baris, column=1, sticky="ew", pady=7
            )

        ttk.Label(
            frame,
            text="Riwayat diabetes orang tua"
        ).grid(row=5, column=0, sticky="w", pady=7)

        ttk.Combobox(
            frame,
            textvariable=self.riwayat,
            values=["Ya", "Tidak"],
            state="readonly"
        ).grid(row=5, column=1, sticky="ew", pady=7)

        tombol = ttk.Frame(frame)
        tombol.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(
            tombol,
            text="Prediksi & Simpan",
            command=self.simpan
        ).pack(side="left", padx=5)

        ttk.Button(
            tombol,
            text="Lihat Data",
            command=self.lihat_data
        ).pack(side="left", padx=5)

        ttk.Button(
            tombol,
            text="Bersihkan",
            command=self.bersihkan
        ).pack(side="left", padx=5)

        self.label_hasil = tk.Label(
            frame,
            text="Hasil prediksi akan tampil di sini",
            font=("Arial", 14, "bold"),
            bg="#eeeeee",
            pady=15
        )
        self.label_hasil.grid(
            row=7, column=0, columnspan=2, sticky="ew"
        )

    def prediksi(self, gula, bmi, riwayat):
        if gula >= 200:
            return "Sangat Tinggi" if bmi >= 30 or riwayat == "Ya" else "Tinggi"

        if gula >= 140:
            return "Tinggi" if bmi >= 30 or riwayat == "Ya" else "Sedang"

        if bmi >= 30:
            return "Sedang" if riwayat == "Ya" else "Waspada"

        return "Waspada" if riwayat == "Ya" else "Rendah"

    def ambil_input(self):
        nama = self.nama.get().strip()

        if not nama:
            raise ValueError("Nama pasien wajib diisi.")

        try:
            usia = int(self.usia.get())
            gula = float(self.gula.get().replace(",", "."))
            bmi = float(self.bmi.get().replace(",", "."))
        except ValueError:
            raise ValueError("Usia, gula darah, dan BMI harus berupa angka.")

        if not 1 <= usia <= 120:
            raise ValueError("Usia harus antara 1 sampai 120 tahun.")

        if not 20 <= gula <= 600:
            raise ValueError("Gula darah harus antara 20 sampai 600 mg/dL.")

        if not 5 <= bmi <= 100:
            raise ValueError("BMI harus antara 5 sampai 100.")

        return nama, usia, gula, bmi, self.riwayat.get()

    def simpan(self):
        try:
            nama, usia, gula, bmi, riwayat = self.ambil_input()
            hasil = self.prediksi(gula, bmi, riwayat)

            self.conn.execute(
                """INSERT INTO pasien
                (nama_pasien, usia, gula_darah, bmi,
                 riwayat_ortu, hasil_prediksi)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (nama, usia, gula, bmi, riwayat, hasil)
            )
            self.conn.commit()

            warna = {
                "Rendah": "#22c55e",
                "Waspada": "#eab308",
                "Sedang": "#f97316",
                "Tinggi": "#ef4444",
                "Sangat Tinggi": "#991b1b"
            }

            self.label_hasil.config(
                text=f"Risiko: {hasil}",
                bg=warna[hasil],
                fg="white"
            )

            messagebox.showinfo(
                "Berhasil",
                "Data pasien berhasil disimpan."
            )

        except ValueError as error:
            messagebox.showwarning("Input tidak valid", str(error))
        except sqlite3.Error as error:
            messagebox.showerror("Database Error", str(error))

    def lihat_data(self):
        jendela = tk.Toplevel(self.root)
        jendela.title("Riwayat Pasien")
        jendela.geometry("850x350")

        kolom = (
            "id", "nama", "usia", "gula",
            "bmi", "riwayat", "hasil"
        )

        tabel = ttk.Treeview(
            jendela,
            columns=kolom,
            show="headings"
        )
        tabel.pack(fill="both", expand=True, padx=10, pady=10)

        judul = [
            "ID", "Nama Pasien", "Usia", "Gula Darah",
            "BMI", "Riwayat Ortu", "Hasil Prediksi"
        ]

        for nama_kolom, teks in zip(kolom, judul):
            tabel.heading(nama_kolom, text=teks)
            tabel.column(nama_kolom, anchor="center", width=110)

        tabel.column("nama", width=170)

        data = self.conn.execute(
            "SELECT * FROM pasien ORDER BY id DESC"
        ).fetchall()

        for baris in data:
            tabel.insert("", "end", values=baris)

    def bersihkan(self):
        self.nama.set("")
        self.usia.set("")
        self.gula.set("")
        self.bmi.set("")
        self.riwayat.set("Tidak")

        self.label_hasil.config(
            text="Hasil prediksi akan tampil di sini",
            bg="#eeeeee",
            fg="black"
        )

    def tutup(self):
        self.conn.close()
        self.root.destroy()


root = tk.Tk()
Aplikasi(root)
root.mainloop()
