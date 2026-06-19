# instalar faster-whisper: pip install faster-whisper
# instalar ffmpeg: https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/


# O script solicita um arquivo específico e trata o caminho no caso de o usuário apenas arrastar o vídeo para o terminal
arquivo_input = input('Insira o caminho do arquivo: ').replace('"','')

print('BASE DE DADOS\n')
# Nota: Recomendo o modelo turbo
bases = ['tiny', 'base', 'small', 'medium', 'large', 'turbo']
for i, b in enumerate(bases):
    print(f'{i+1} - {b}')
x = int(input('\nEscolha uma base: '))

import os
from faster_whisper import WhisperModel # Alterado
import random

# ALTERAÇÃO: A função format foi atualizada para extrair as frações de segundo (milissegundos) corretamente,
# evitando que várias palavras fiquem marcadas no mesmo segundo com final ",000".
def format(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int(round((s - int(s)) * 1000))
    return f'{h:02d}:{m:02d}:{sec:02d},{ms:03d}'



# Separa a pasta raiz do nome do arquivo
pasta = os.path.dirname(arquivo_input)
arquivo_nome = os.path.basename(arquivo_input)

# Muda para o diretório onde o arquivo está, caso o caminho contenha diretórios
if pasta:
    os.chdir(pasta)

# A lista de arquivos (mkvs) armazena apenas o único arquivo selecionado, pode ser modificado para legendar em lote
mkvs = [arquivo_nome]

# Inicializa o modelo fora do loop para não recarregar toda a hora
# Usamos device="cpu" e compute_type="int8" para máxima compatibilidade e velocidade em AMD/Windows, o meu caso
modelo = WhisperModel(bases[x-1], device="cpu", compute_type="int8") 

for y in range(len(mkvs)):
    try:
        os.system('title Transcrever arquivo')
        os.system('cls')
        
        print('TRANSCREVER ARQUIVO\n')
        print('\nBase escolhida: ', bases[x-1])
        print('\n\n')
        os.system('cls')

        print('TRANSCREVER ARQUIVO\n')
        print('ARQUIVO\n')
        arquivos = mkvs
        
        y_idx = y

        # Verifica se o arquivo .lrc já existe na respetiva subpasta
        if os.path.exists(f'{arquivos[y_idx][:-4]}.lrc'):
            continue
        
        print((bases[x-1]).upper(), (arquivos[y_idx]).upper())

        # ALTERAÇÃO: O parâmetro word_timestamps=True foi adicionado para que o modelo
        # devolva o tempo exato de início e fim de cada palavra.
        segments_gen, info = modelo.transcribe(
            arquivos[y_idx],
            word_timestamps=True, 
            language="pt",
            #beam_size=5,
            )
        segments = list(segments_gen) # Converte para lista para usar nos loops abaixo
        
        print('\n\n')
        os.system('cls')

        print('Texto: ')
        # No faster-whisper, montamos o texto completo a partir dos segmentos
        resposta = "".join([s.text for s in segments])
        print(resposta)
        
        # --- TXT ---
        if False:
            text = ''
            for d in segments:
                text += f'{d.text.strip()}\n' 

            with open(f'{arquivos[y_idx][:-4]}.txt','w', encoding='utf-8') as txt:
                # Salva o arquivo
                txt.write(text)
            
        # --- SRT ---
        if True:
            sub = ''
            contador_srt = 1 
            for d in segments:
                # Em vez de fazer divisões matemáticas, iteramos diretamente
                # sobre a lista de palavras (d.words) que o Whisper gerou com tempos precisos.
                if d.words: # Verifica se existem palavras no segmento
                    for word_info in d.words:
                        palavra = word_info.word.strip()
                        
                        if palavra: # Ignora possíveis espaços vazios devolvidos
                            # word_info.start e word_info.end contêm o tempo exato em que a palavra foi dita
                            sub += f'{contador_srt}\n{format(word_info.start)} --> {format(word_info.end)}\n{palavra}\n\n'
                            contador_srt += 1

            with open(f'{arquivos[y_idx][:-4]}.srt', 'w', encoding='utf-8') as srt_file:
                # ALTERAÇÃO: Salva o SRT
                srt_file.write(sub)

        # --- LRC ---
        if True:
            lrc = ''
            for d in segments:
                # ALTERAÇÃO: A mesma lógica baseada nos timestamps nativos é aplicada ao LRC
                if d.words:
                    for word_info in d.words:
                        palavra = word_info.word.strip()
                        
                        if palavra:
                            # Utiliza o tempo de início exato da palavra
                            minutos = int(word_info.start // 60)
                            segundos = word_info.start % 60
                            lrc += f'[{minutos:02d}:{segundos:05.2f}] {palavra}\n'

            # O arquivo .lrc será salvo na mesma subpasta do arquivo original
            with open(f'{arquivos[y_idx][:-4]}.lrc', 'w', encoding='utf-8') as lrc_file:
                lrc_file.write(lrc)
                
            print('\a') 
            
    except Exception as e:
        print(f"Erro ao processar {arquivos[y]}: {e}")
        pass
