
import sys
import os
import platform
from typing import Optional
from ..normalizer.normalizer import Normalizer

class Helper:
    """
    Classe helper para interfaces CLI e GUI cross-platform
    """
    
    def __init__(self):
        self.normalizer = Normalizer()
    
    def cli_interface(self, args: Optional[list] = None) -> int:
        """
        Interface de linha de comando para Unix/Linux
        
        Args:
            args: Lista de argumentos da linha de comando (opcional)
            
        Returns:
            int: Código de saída (0 = sucesso, 1 = erro)
        """
        if args is None:
            args = sys.argv[1:]
        
        if len(args) != 1:
            print("Usage: python main.py <ofx_file>")
            return 1
        
        input_file = args[0]
        
        if not os.path.isfile(input_file):
            print(f"File not found: {input_file}")
            return 1
        
        try:
            output_file = self.normalizer.normalize_ofx_file(input_file)
            print(f"Normalized OFX file written to: {output_file}")
            return 0
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return 1
    
    def gui_interface(self) -> None:
        """
        Interface gráfica para Windows usando CustomTkinter
        """
        try:
            import customtkinter as ctk
            from tkinter import filedialog, messagebox
        except ImportError:
            print("CustomTkinter not installed. Please install it with: pip install customtkinter")
            return
        
        # Configuração do tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        class OFXNormalizerGUI:
            def __init__(self):
                self.root = ctk.CTk()
                self.root.title("OFX Normalizer - NokTech")
                self.root.geometry("600x400")
                self.root.resizable(True, True)
                
                self.normalizer = Normalizer()
                self.setup_ui()
            
            def setup_ui(self):
                # Frame principal
                main_frame = ctk.CTkFrame(self.root)
                main_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Título
                title_label = ctk.CTkLabel(
                    main_frame, 
                    text="OFX Normalizer", 
                    font=ctk.CTkFont(size=24, weight="bold")
                )
                title_label.pack(pady=(20, 10))
                
                # Subtítulo
                subtitle_label = ctk.CTkLabel(
                    main_frame,
                    text="Normalize OFX files for Microsoft Money compatibility",
                    font=ctk.CTkFont(size=14)
                )
                subtitle_label.pack(pady=(0, 30))
                
                # Frame para seleção de arquivo
                file_frame = ctk.CTkFrame(main_frame)
                file_frame.pack(fill="x", padx=20, pady=10)
                
                # Label do arquivo
                self.file_label = ctk.CTkLabel(
                    file_frame,
                    text="No file selected",
                    font=ctk.CTkFont(size=12)
                )
                self.file_label.pack(pady=10)
                
                # Botão para selecionar arquivo
                select_button = ctk.CTkButton(
                    file_frame,
                    text="Select OFX File",
                    command=self.select_file,
                    font=ctk.CTkFont(size=14)
                )
                select_button.pack(pady=10)
                
                # Botão para processar
                self.process_button = ctk.CTkButton(
                    main_frame,
                    text="Normalize File",
                    command=self.process_file,
                    state="disabled",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    height=40
                )
                self.process_button.pack(pady=20)
                
                # Área de log
                log_frame = ctk.CTkFrame(main_frame)
                log_frame.pack(fill="both", expand=True, padx=20, pady=10)
                
                log_label = ctk.CTkLabel(
                    log_frame,
                    text="Processing Log:",
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                log_label.pack(anchor="w", padx=10, pady=(10, 5))
                
                self.log_text = ctk.CTkTextbox(
                    log_frame,
                    height=150,
                    font=ctk.CTkFont(size=11)
                )
                self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
                
                # Variável para armazenar o arquivo selecionado
                self.selected_file = None
            
            def select_file(self):
                """Selecionar arquivo OFX"""
                file_path = filedialog.askopenfilename(
                    title="Select OFX File",
                    filetypes=[("OFX files", "*.ofx"), ("All files", "*.*")]
                )
                
                if file_path:
                    self.selected_file = file_path
                    filename = os.path.basename(file_path)
                    self.file_label.configure(text=f"Selected: {filename}")
                    self.process_button.configure(state="normal")
                    self.log_message(f"File selected: {file_path}")
            
            def log_message(self, message):
                """Adicionar mensagem ao log"""
                self.log_text.insert("end", f"{message}\n")
                self.log_text.see("end")
                self.root.update()
            
            def process_file(self):
                """Processar arquivo OFX"""
                if not self.selected_file:
                    messagebox.showerror("Error", "No file selected")
                    return
                
                try:
                    self.log_message("Starting normalization process...")
                    self.process_button.configure(state="disabled", text="Processing...")
                    
                    output_file = self.normalizer.normalize_ofx_file(self.selected_file)
                    
                    self.log_message(f"✓ Normalization completed successfully!")
                    self.log_message(f"✓ Output file: {output_file}")
                    
                    messagebox.showinfo(
                        "Success", 
                        f"File normalized successfully!\n\nOutput: {os.path.basename(output_file)}"
                    )
                    
                except Exception as e:
                    error_msg = f"Error processing file: {str(e)}"
                    self.log_message(f"✗ {error_msg}")
                    messagebox.showerror("Error", error_msg)
                
                finally:
                    self.process_button.configure(state="normal", text="Normalize File")
            
            def run(self):
                """Executar a interface gráfica"""
                self.root.mainloop()
        
        # Criar e executar a GUI
        app = OFXNormalizerGUI()
        app.run()
    
    def run_appropriate_interface(self) -> int:
        """
        Detecta argumentos e sistema operacional para executar a interface apropriada
        
        Returns:
            int: Código de saída (0 = sucesso, 1 = erro)
        """
        # Se há argumentos na linha de comando, sempre usar CLI
        if len(sys.argv) > 1:
            return self.cli_interface()
        
        # Se não há argumentos, verificar sistema operacional
        system = platform.system().lower()
        
        if system == "windows":
            # Interface gráfica para Windows quando não há argumentos
            self.gui_interface()
            return 0
        else:
            # Interface CLI para Unix/Linux (mostra usage)
            return self.cli_interface()