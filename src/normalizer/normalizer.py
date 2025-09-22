import re
import os
from ..config.config import Config

class Normalizer:

    def __init__(self):
        # Classe construtora da normalização
        # Chama o config
        self.config = Config()
        # Limite máximo para o campo <NAME> compatível com Microsoft Money
        self.MAX_NAME_LEN = self.config.MAX_NAME_LEN
    
    @staticmethod
    def _read_text_with_fallback(path: str):
        """Lê o arquivo em binário e tenta decodificar com diferentes codificações"""
        data = open(path, 'rb').read()
        for enc in ('utf-8-sig', 'utf-8', 'cp1252'):
            try:
                return data.decode(enc), enc
            except UnicodeDecodeError:
                continue
        return data.decode('latin-1', errors='replace'), 'latin-1'

    @staticmethod
    def _strip_control_chars(s: str) -> str:
        """Remove caracteres de controle ASCII (exceto TAB, CR, LF)."""
        return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", s)
        
    @staticmethod
    def _normalize_date_line(line: str) -> str:
        """Remove timezone sufixos como [-3:BRT] mantendo apenas 14 dígitos"""
        return re.sub(r'<(DTSERVER|DTSTART|DTEND|DTPOSTED)>(\d{14})(\[[^\]]+\])?',
                    lambda m: f'<{m.group(1)}>{m.group(2)}', line)

    def _fix_stmttrn_block(self, block_lines):
        """Reordenar para que <NAME> venha antes de <MEMO> e garantir limite de tamanho"""
        name_idx = next((i for i, l in enumerate(block_lines) if l.strip().startswith('<NAME>')), None)
        memo_idx = next((i for i, l in enumerate(block_lines) if l.strip().startswith('<MEMO>')), None)

        # Ajuste de tamanho do <NAME>
        if name_idx is not None:
            raw = block_lines[name_idx]
            # Extrair valor de NAME (com ou sem fechamento)
            m = re.search(r'<NAME>(.*?)</NAME>', raw)
            if m:
                name_val = m.group(1)
            else:
                m2 = re.search(r'<NAME>(.*)', raw)
                name_val = m2.group(1).strip() if m2 else ''
            clean_name = self._strip_control_chars(name_val)
            if clean_name:
                if len(clean_name) > self.MAX_NAME_LEN:
                    head = clean_name[:self.MAX_NAME_LEN].rstrip()
                    tail = clean_name[self.MAX_NAME_LEN:].lstrip()
                    # Atualiza NAME com valor truncado e fechamento explícito
                    block_lines[name_idx] = f'<NAME>{head}</NAME>'
                    # Anexa excedente ao MEMO
                    if memo_idx is not None:
                        memo_raw = block_lines[memo_idx]
                        mm = re.search(r'<MEMO>(.*?)</MEMO>', memo_raw)
                        if mm:
                            memo_val = mm.group(1)
                            new_memo = (memo_val + ' ' + tail).strip()
                        else:
                            new_memo = tail
                        block_lines[memo_idx] = f'<MEMO>{new_memo}</MEMO>'
                    else:
                        # Insere MEMO logo após NAME com o excedente
                        block_lines.insert(name_idx + 1, f'<MEMO>{tail}</MEMO>')
                        # Recalcula memo_idx para possível reordenação
                        memo_idx = next((i for i, l in enumerate(block_lines) if l.strip().startswith('<MEMO>')), None)
                else:
                    # Normaliza fechamento explícito
                    block_lines[name_idx] = f'<NAME>{clean_name}</NAME>'

        # Reordenar NAME antes de MEMO
        name_idx = next((i for i, l in enumerate(block_lines) if l.strip().startswith('<NAME>')), None)
        memo_idx = next((i for i, l in enumerate(block_lines) if l.strip().startswith('<MEMO>')), None)
        if name_idx is not None and memo_idx is not None and name_idx > memo_idx:
            name_line = block_lines.pop(name_idx)
            memo_idx = next((i for i, l in enumerate(block_lines) if l.strip().startswith('<MEMO>')), None)
            block_lines.insert(memo_idx, name_line)
        return block_lines

    def normalize_ofx_file(self, in_path: str) -> str:
        """
        Normaliza um arquivo OFX para compatibilidade com Microsoft Money
        
        Args:
            in_path (str): Caminho para o arquivo OFX de entrada
            
        Returns:
            str: Caminho para o arquivo OFX normalizado gerado
            
        Raises:
            FileNotFoundError: Se o arquivo de entrada não for encontrado
        """
        if not os.path.isfile(in_path):
            raise FileNotFoundError(f'File not found: {in_path}')

        text, src_enc = self._read_text_with_fallback(in_path)
        lines = text.splitlines()

        out_lines = []

        # Remoção robusta de bloco <BALLIST>...</BALLIST>, apenas se ambos aparecerem
        in_ballist = False
        ballist_buffer = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Ajuste de header ENCODING/CHARSET quando presentes
            if 'ENCODING:UTF-8' in line:
                line = 'ENCODING:USASCII'
            if 'CHARSET:NONE' in line:
                line = 'CHARSET:1252'

            # Normalizar datas removendo timezone + remover controles
            line = self._strip_control_chars(self._normalize_date_line(line))

            # Remoção segura de bloco <BALLIST> ... </BALLIST>
            if '<BALLIST>' in line:
                in_ballist = True
                ballist_buffer.append(line)
                i += 1
                continue
            if in_ballist:
                ballist_buffer.append(line)
                if '</BALLIST>' in line:
                    # Encontrou fechamento: descarta todo o buffer
                    in_ballist = False
                    ballist_buffer.clear()
                i += 1
                continue

            # Reordenação e saneamento dentro do bloco <STMTTRN> ... </STMTTRN>
            if line.strip() == '<STMTTRN>':
                block = [line]
                i += 1
                # Coletar até o fechamento (ou fim seguro)
                while i < len(lines):
                    cur = self._strip_control_chars(self._normalize_date_line(lines[i]))
                    block.append(cur)
                    if cur.strip() == '</STMTTRN>':
                        break
                    i += 1
                # Processar saneamento + reordenação NAME antes de MEMO (mantém demais intacto)
                if len(block) >= 3:
                    head = block[0]
                    tail = block[-1]
                    middle = block[1:-1]
                    middle = self._fix_stmttrn_block(middle)
                    block = [head] + middle + [tail]
                out_lines.extend(block)
                i += 1
                continue

            out_lines.append(line)
            i += 1

        # Se terminou arquivo ainda dentro de <BALLIST>, devolve buffer ao output (não remove sem fechamento)
        if in_ballist and ballist_buffer:
            out_lines.extend(ballist_buffer)

        # Garantir CRLF e coerência de codificação (CP1252)
        out_text = '\r\n'.join(out_lines) + '\r\n'

        base, ext = os.path.splitext(in_path)
        out_path = f"{base}_money{ext if ext else '.ofx'}"
        with open(out_path, 'w', encoding='cp1252', newline='\r\n', errors='replace') as f:
            f.write(out_text)

        return out_path

    