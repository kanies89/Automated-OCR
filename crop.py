from tkinter import *
from io import BytesIO
from PIL import ImageGrab, ImageTk
import pytesseract

pytesseract.pytesseract.tesseract_cmd= r'C:\Program Files\Tesseract-OCR\tesseract'

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Cropper")
        self.image_path = ""
        self.x = 0
        self.y = 0
        self.crop_rect = None
        self.language = "eng"

        # Create a scrollbar and canvas
        self.scrollbar = Scrollbar(self.master)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas = Canvas(self.master, width=400, height=400, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)
        self.scrollbar.config(command=self.canvas.yview)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.on_release(event, self.language))

        self.button_open = Button(self.master, text="Open", command=self.open_image)
        self.button_open.pack(side=TOP)

        # Add language selection button
        langmenu = Menu(self.master, tearoff=0)
        self.master.config(menu=langmenu)
        langmenu.add_command(label="English", command=lambda: self.set_language("eng"))
        langmenu.add_command(label="Polish", command=lambda: self.set_language("pol"))

    def set_language(self, lang):
        self.language = lang

    def on_press(self, event):
        self.x = self.canvas.canvasx(event.x)
        self.y = self.canvas.canvasy(event.y)
        self.crop_rect = None

    def on_drag(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self.crop_rect = self.canvas.create_rectangle(self.x, self.y, x, y, outline="red")

    def on_release(self, event, language):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        box = (self.x, self.y, x, y)
        cropped_image = self.image.crop(box)
        # Calculate the size of the red outline
        width = abs(x - self.x)
        height = abs(y - self.y)
        # Pass the size of the red outline and language to the crop method
        box = (self.x, self.y, self.x + width, self.y + height)
        cropped_image = self.image.crop(box)
        cropped_image.save("cropped_image.jpg")
        crop_text = pytesseract.image_to_string(cropped_image, lang=language)
        print(crop_text)

    def open_image(self):
        # Grab image from clipboard
        root = Tk()
        root.withdraw()
        image = ImageGrab.grabclipboard()
        if image:
            self.image = image.convert("RGB")
            self.photo = ImageTk.PhotoImage(self.image)

            # Resize canvas to match image size
            self.canvas.config(width=self.photo.width(), height=self.photo.height())

            # Resize window to match canvas size
            self.master.geometry("{}x{}".format(self.photo.width(), self.photo.height()))

            self.canvas.create_image(0, 0, anchor=NW, image=self.photo)


root = Tk()
app = App(root)
root.mainloop()
