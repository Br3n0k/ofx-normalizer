import sys
import os
import re

# Definição do limite máximo para o campo <NAME> compatível com Microsoft Money
MAX_NAME_LEN = 32


def _read_text_with_fallback(path: str):
    data = open(path, 'rb').read()
    for enc in ('utf-8-sig', 'utf-8', 'cp1252'):
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return data.decode('latin-1', errors='replace'), 'latin-1'


def _strip_control_chars(s: str) -> str:
    """Remove caracteres de controle ASCII (exceto TAB, CR, LF)."""
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", s)


def _normalize_date_line(line: str) -> str:
    # Remove timezone sufixos como [-3:BRT] mantendo apenas 14 dígitos
    return re.sub(r'<(DTSERVER|DTSTART|DTEND|DTPOSTED)>(\d{14})(\[[^\]]+\])?',
                  lambda m: f'<{m.group(1)}>{m.group(2)}', line)


def _fix_stmttrn_block(block_lines):
    # Reordenar para que <NAME> venha antes de <MEMO> e garantir limite de tamanho
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
        clean_name = _strip_control_chars(name_val)
        if clean_name:
            if len(clean_name) > MAX_NAME_LEN:
                head = clean_name[:MAX_NAME_LEN].rstrip()
                tail = clean_name[MAX_NAME_LEN:].lstrip()
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


def main():
    if len(sys.argv) != 2:
        print('É necessário fornecer o arquivo OFX a ser corrigido.\nExemplo: python quebra.py caminho/arquivo.ofx')
        return

    in_path = sys.argv[1]
    if not os.path.isfile(in_path):
        print('Arquivo não encontrado:', in_path)
        return

    text, src_enc = _read_text_with_fallback(in_path)
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
        line = _strip_control_chars(_normalize_date_line(line))

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
                cur = _strip_control_chars(_normalize_date_line(lines[i]))
                block.append(cur)
                if cur.strip() == '</STMTTRN>':
                    break
                i += 1
            # Processar saneamento + reordenação NAME antes de MEMO (mantém demais intacto)
            if len(block) >= 3:
                head = block[0]
                tail = block[-1]
                middle = block[1:-1]
                middle = _fix_stmttrn_block(middle)
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

    print('Arquivo corrigido gerado em:', out_path)


if __name__ == '__main__':
    main()