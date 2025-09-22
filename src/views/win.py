import customtkinter as ctk
from ..helpers.helper import Helper

# configuração da aparencia
ctk.set_appearance_mode("dark")

#criação da janela principal
app = ctk.CTk()

app.title("OFX Normalizer")
app.geometry("800x600")

# criação do frame principal
frame = ctk.CTkFrame(app)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# criação do label
label = ctk.CTkLabel(frame, text="OFX Normalizer", font=("Arial", 24))
label.pack(pady=20)

# criação do botão
button = ctk.CTkButton(frame, text="Normalizar OFX", font=("Arial", 16))
button.pack(pady=20)

# execução da aplicação
app.mainloop()
