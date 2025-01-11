import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import fitz  

class PDFSignatureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng Dụng Dán Chữ Ký vào PDF")

        self.pdf_path = None
        self.signature_path = None
        self.current_page = 0

        self.pdf_width = 0
        self.pdf_height = 0
        self.canvas_width = 1000
        self.canvas_height = 750

        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="lightcoral")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        self.upload_pdf_button = tk.Button(root, text="Chọn File PDF", command=self.filepdf_pdf, activebackground="red", bg="gray", fg="gold")
        self.upload_pdf_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.upload_signature_button = tk.Button(root, text="Chọn Hình Ảnh Chữ Ký", command=self.hinhanh_signature, activebackground="red", bg="gray", fg="gold")
        self.upload_signature_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_button = tk.Button(root, text="Lưu PDF", command=self.save_pdf, activebackground="red", bg="gray", fg="gold")
        self.save_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.next_page_button = tk.Button(root, text="Trang Kế", command=self.tien_page, activebackground="red", bg="gray", fg="gold")
        self.next_page_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.prev_page_button = tk.Button(root, text="Trang Trước", command=self.lui_page, activebackground="red", bg="gray", fg="gold")
        self.prev_page_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.signature_image = None
        self.signature_tk = None
        self.signature_position = None

        self.canvas.bind("<B1-Motion>", self.move_signature)
        self.canvas.bind("<ButtonRelease-1>", self.place_signature)

    def filepdf_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.pdf_path:
            self.render_page()

    def hinhanh_signature(self):
     self.signature_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
     if self.signature_path:
        self.signature_image = Image.open(self.signature_path)
        
        # Chuyển đổi hình ảnh sang PNG
        png_signature_path = "temp_signature.png"
        self.signature_image.save(png_signature_path, format="PNG")

        self.signature_image.thumbnail((100, 100))
        self.signature_tk = ImageTk.PhotoImage(self.signature_image)
        self.signature_position = None
        self.canvas.create_image(50, 50, image=self.signature_tk, anchor=tk.NW, tags="signature")
        
        # Lưu đường dẫn PNG mới
        self.signature_path = png_signature_path


    def render_page(self):
        if self.pdf_path:
            doc = fitz.open(self.pdf_path)
            if self.current_page < 0:
                self.current_page = 0
            elif self.current_page >= len(doc):
                self.current_page = len(doc) - 1

            page = doc[self.current_page]
            self.pdf_width, self.pdf_height = page.rect.width, page.rect.height

            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Thay Image.ANTIALIAS bằng Image.Resampling.LANCZOS
            img = img.resize((self.canvas_width, self.canvas_height), Image.Resampling.LANCZOS)

            self.page_tk = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.page_tk, anchor=tk.NW, tags="page")

    def move_signature(self, event):
        if self.signature_tk:
            self.canvas.delete("signature")
            self.signature_position = (event.x, event.y)
            self.canvas.create_image(event.x, event.y, image=self.signature_tk, anchor=tk.CENTER, tags="signature")

    def place_signature(self, event):
        self.signature_position = (event.x, event.y)

    def save_pdf(self):
        if not self.pdf_path or not self.signature_path or not self.signature_position:
            print("Error: Missing PDF, signature, or position.")
            return

        x_canvas, y_canvas = self.signature_position
        x_pdf = x_canvas * self.pdf_width / self.canvas_width
        y_pdf = y_canvas * self.pdf_height / self.canvas_height

        try:
            doc = fitz.open(self.pdf_path)
            page = doc[self.current_page]

            rect = fitz.Rect(x_pdf - 50, y_pdf - 50, x_pdf + 50, y_pdf + 50)
            page.insert_image(rect, filename=self.signature_path)

            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
            if save_path:
                doc.save(save_path)
                print("PDF đã được lưu thành công.")
            doc.close()
        except Exception as e:
            print(f"Lỗi khi lưu PDF: {e}")

    def tien_page(self):
        self.current_page += 1
        self.render_page()

    def lui_page(self):
        self.current_page -= 1
        self.render_page()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSignatureApp(root)
    root.mainloop()
