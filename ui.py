from tkinter import *
from PIL import ImageGrab, ImageTk
import pytesseract
import os
import openai
import cv2


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


class ImageOCRApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image OCR")
        self.master.geometry("1400x800")  # set window size to 1200x1000
        self.language = "eng"
        self.init_topbar()
        self.init_canvas()
        self.question = ""
        self.answer = "None"
        self.image_name = "cropped_image.jpg"

    def init_topbar(self):
        # Create a menubar
        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        # Create a top bar frame
        self.topbar_frame = Frame(self.master)
        self.topbar_frame.pack(side=TOP, fill=X)

        # create two frames inside topbar
        left_frame = Frame(self.topbar_frame)
        left_frame.pack(side=LEFT, fill=X, expand=True)
        right_frame = Frame(self.topbar_frame)
        right_frame.pack(side=RIGHT, fill=X, expand=True)

        # ChatGPT response label
        self.response_label = Label(left_frame, text="ChatGPT: waiting for input...", anchor=W, wraplength=400)
        self.response_label.pack(side=LEFT, padx=10, pady=5, fill=X, expand=True)

        # Create a "Open" button
        self.new_button = Button(right_frame, text="Open", command=self.open_image)
        self.new_button.pack(side=LEFT, padx=5)

        # Create a "Language" menu
        langmenu = Menu(right_frame, tearoff=0)
        langmenu.add_command(label="Eng", command=lambda: self.set_language("eng"))
        langmenu.add_command(label="Pol", command=lambda: self.set_language("pol"))

        langmenu_button = Menubutton(right_frame, text="Language", menu=langmenu)
        langmenu_button.pack(side=LEFT, padx=5)

        # Create language selection buttons
        self.create_language_selection_buttons()

        # Create an OCR text widget
        self.ocr_text = Text(right_frame, width=50, height=5)
        self.ocr_text.pack(side=LEFT, padx=5, pady=5, fill=X, expand=True)

        # Create a "Send" button for sending OCR text to ChatGPT
        send_button = Button(right_frame, text="Send", command=self.send_ocr_text)
        send_button.pack(side=LEFT, padx=5)

    def init_canvas(self):
        # Create a scrollbar and canvas
        self.scrollbar_x = Scrollbar(self.master, orient=HORIZONTAL)
        self.scrollbar_x.pack(side=BOTTOM, fill=X)
        self.scrollbar_y = Scrollbar(self.master)
        self.scrollbar_y.pack(side=RIGHT, fill=Y)
        self.canvas = Canvas(self.master, xscrollcommand=self.scrollbar_x.set, yscrollcommand=self.scrollbar_y.set)
        self.canvas.pack(side=LEFT, expand=False, fill=BOTH)
        self.scrollbar_x.config(command=self.canvas.xview)
        self.scrollbar_y.config(command=self.canvas.yview)

        # Bind mouse events to the canvas
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda event: self.on_release(event, self.language))
        self.canvas.bind("<MouseWheel>", self.on_scroll)

    def create_language_selection_buttons(self):
        # Create language selection buttons
        self.language_buttons = []
        for i, label in enumerate(["Eng", "Pol"]):
            button = Button(self.topbar_frame, text=label, command=lambda lang=label.lower(): self.set_language(lang))
            button.pack(side=LEFT, padx=5)
            self.language_buttons.append(button)

            if label.lower() == self.language:
                self.language_buttons[i].config(bg="light blue")
    def send_ocr_text(self):
        # Get the OCR text from the Text widget
        ocr_text = self.ocr_text.get("1.0", "end-1c")

        # Send the OCR text to ChatGPT
        self.question = ocr_text
        self.ask_chatgpt()

    def set_language(self, lang):
        for i, label in enumerate(["Eng", "Pol"]):
            if label.lower() == lang:
                self.language = lang
                self.language_buttons[i].config(bg="light blue")
            else:
                self.language_buttons[i].config(bg=self.topbar_frame.cget("bg"))

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

        # Calculate the size of the red outline
        width = abs(x - self.x)
        height = abs(y - self.y)

        # Pass the size of the red outline and language to the crop method
        box = (self.x, self.y, self.x + width, self.y + height)

        cropped_image = self.image.crop(box)

        cropped_image.save(self.image_name)
        processed_image = self.preprocess_image()
        cv2.imwrite(self.image_name, processed_image)

        crop_text = pytesseract.image_to_string(self.image_name, lang=language)

        # Update the OCR text in the Text widget
        self.ocr_text.delete("1.0", "end")
        self.ocr_text.insert("end", crop_text)
        print(crop_text)

    def on_scroll(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def open_image(self):
        # Grab image from clipboard
        root = Tk()
        root.withdraw()
        image = ImageGrab.grabclipboard()
        if image:
            self.image = image.convert("RGB")

            # Resize canvas to match image size
            self.canvas.config(width=self.image.width, height=self.image.height)

            # Resize window to match canvas size
            self.master.geometry("{}x{}".format(self.canvas.winfo_width(), self.canvas.winfo_height()))

            # Create PhotoImage object using PIL image
            self.photo = ImageTk.PhotoImage(self.image)

            # Add image to canvas
            self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

            # Enable scrolling
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def preprocess_image(self):
        # Load image
        img = cv2.imread(self.image_name)

        # Convert from RGB to LAB color space
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)

        # Split L, A, B channels
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_clahe = clahe.apply(l)

        # Merge L, A, B channels back to LAB image
        lab_clahe = cv2.merge((l_clahe, a, b))

        # Convert back to RGB color space
        rgb_clahe = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2RGB)

        # Binarize image
        gray = cv2.cvtColor(rgb_clahe, cv2.COLOR_RGB2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Denoise image
        denoised = cv2.medianBlur(thresh, 3)

        return denoised

    def ask_chatgpt(self):
        if not self.question:
            return

        openai.api_key = os.environ["OPENAI_API_KEY"]
        MODEL = "gpt-3.5-turbo"
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are performing text analysis."},
                {"role": "user", "content": "YOUR PROMPT GOES HERE: " + self.question},
            ],
            temperature=0,
            max_tokens=250,
        )

        self.answer = response['choices'][0]['message']['content']

        # Update response label
        self.response_label.config(text=f"ChatGPT: {self.answer}")

        # print chat response
        print(f"ChatGPT: {self.answer}")