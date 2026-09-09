import logging
import sys
from pathlib import Path

class LayerLogger:
    def __init__(self, layer_name: str):
        self.layer_name = layer_name.strip().lower()
        self.formatter = self._create_formatter()
        
        # Garante o salvamento físico estrito em src/logs, não importa onde seja chamado
        BASE_DIR = Path(__file__).resolve().parent
        self.path = BASE_DIR / f"{self.layer_name}.log"
        
        self.logger = logging.getLogger(f"layer.{self.layer_name}")

    def _create_formatter(self) -> logging.Formatter:
        """Define o formato visual padrão das mensagens de log."""
        return logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def _add_console_handler(self):
        """Configura a saída para sys.stderr para evitar captação de frameworks de teste."""
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self):
        """Configura a gravação direta no arquivo gerado pelo Path."""
        file_handler = logging.FileHandler(self.path, encoding='utf-8')
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def _configure_logger(self):
        """Aplica as configurações básicas e limpa handlers antigos."""
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self._add_console_handler()
        self._add_file_handler()

    def build(self) -> logging.Logger:
        """Orquestra a configuração completa e retorna o logger pronto para uso."""
        self._configure_logger()
        return self.logger
