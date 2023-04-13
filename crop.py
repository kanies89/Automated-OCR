from tkinter import *
from PIL import Image, ImageGrab, ImageTk
import pytesseract
import pyperclip

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Image OCR")
        self.image_path = ""
        self.x = 0
        self.y = 0
        self.crop_rect = None
        self.language = "eng"
        self.initUI()

        # Create a scrollbar and canvas
        self.scrollbar = Scrollbar(self.master)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas = Canvas(self.master, width=400, height=400, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)
        self.scrollbar.config(command=self.canvas.yview)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.on_release(event, self.language))

    def initUI(self):

        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        # Top bar
        self.topbar = Frame(self.master)
        self.topbar.pack(side=TOP, fill=X)

        # Language selection menu
        langmenu = Menu(self.topbar, tearoff=0)
        langmenu.add_command(label="Eng", command=lambda: self.set_language("eng"))
        langmenu.add_command(label="Pol", command=lambda: self.set_language("pol"))

        langmenu_button = Menubutton(self.topbar, text="Language", menu=langmenu)
        langmenu_button.pack(side=RIGHT, padx=5)

        # Button frame
        button_frame = Frame(self.topbar)
        button_frame.pack(side=LEFT, padx=10, pady=5)

        # "Open" button
        self.new_button = Button(button_frame, text="Open", command=self.open_image)
        self.new_button.pack(side=LEFT, padx=5)

        self.language_buttons = []

        for i, label in enumerate(["Eng", "Pol"]):
            button = Button(self.topbar, text=label, command=lambda lang=label.lower(): self.set_language(lang))
            button.pack(side=LEFT, padx=5)
            self.language_buttons.append(button)

            if label.lower() == self.language:
                self.language_buttons[i].config(bg="light blue")

    def set_language(self, lang):
        for i, label in enumerate(["Eng", "Pol"]):
            if label.lower() == lang:
                self.language = lang
                self.language_buttons[i].config(bg="light blue")
            else:
                self.language_buttons[i].config(bg=self.topbar.cget("bg"))

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
        # copy to clipboard
        pyperclip.copy(crop_text)
        print(crop_text)


    def open_image(self):
        # Grab image from clipboard
        root = Tk()
        root.withdraw()
        image = ImageGrab.grabclipboard()
        if image:
            self.image = image.convert("RGB")

            # Resize image to 50%
            self.image = self.image.resize((int(self.image.width * 0.5), int(self.image.height * 0.5)), Image.LANCZOS)

            self.photo = ImageTk.PhotoImage(self.image)

            # Resize canvas to match image size
            self.canvas.config(width=self.photo.width(), height=self.photo.height())

            # Resize window to match canvas size
            self.master.geometry("{}x{}".format(self.photo.width(), self.photo.height()))

            self.canvas.create_image(0, 0, anchor=NW, image=self.photo)


root = Tk()
app = App(root)
root.mainloop()
