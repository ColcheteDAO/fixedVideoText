import re
import os
import argparse
import glob
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def process_video(input_path, output_path, args):
    print(f"Processando vídeo: {input_path}")
    video = VideoFileClip(input_path)
    
    # Lógica de corte (subclip)
    start = args.start_time if args.start_time else 0
    
    if str(args.end_time) == "-1":
        end = video.duration
    else:
        end = args.end_time if args.end_time else video.duration
        
    if args.start_time or args.end_time:
        video = video.subclip(start, end)
    
    w, h = video.size
    
    # Margens relativas ao tamanho do vídeo (ex: 5% e 8%)
    padding_left = int(w * 0.05)
    padding_bottom = int(h * 0.08)
    max_text_width = int(w * 0.85)
    
    # Tamanhos de fonte proporcionais à altura do vídeo
    fontsize_word = int(h * 0.042)
    fontsize_pos = int(h * 0.04)
    fontsize_def = int(h * 0.045)
    
    try:
        # Texto 1: A Palavra (Fonte Maior)
        clip_word = TextClip(
            args.word, 
            font=args.font_word, 
            fontsize=fontsize_word, 
            color='white', 
            align='West'
        )
        
        # Texto 2: Classe Gramatical
        clip_pos = TextClip(
            args.pos, 
            font=args.font_pos, 
            fontsize=fontsize_pos, 
            color='white', 
            align='West'
        )
        
        # Texto 3: Definição (Word wrap automático usando method='caption' e argumento size)
        clip_def = TextClip(
            args.definition, 
            font=args.font_def, 
            fontsize=fontsize_def, 
            color='white',
            method='caption', 
            size=(max_text_width, None), 
            align='West'
        )
    except Exception as e:
        print(f"Erro ao gerar textos (verifique se as fontes .ttf informadas existem e são válidas): {e}")
        return

    # Calcular o eixo Y a partir do centro vertical para o primeiro texto
    y_word = int((h - clip_word.h) / 2)
    y_pos = y_word + clip_word.h - int(h * 0.025)
    y_def = y_pos + clip_pos.h - int(h * 0.025)
    
    # Aplicar posicionamento e duração (mesma duração do vídeo cortado)
    clip_word = clip_word.set_position((padding_left, y_word)).set_duration(video.duration)
    # Desloca a classe gramatical ligeiramente para a esquerda para compensar a margem da fonte cursiva
    clip_pos = clip_pos.set_position((padding_left - int(w * 0.002), y_pos)).set_duration(video.duration)
    clip_def = clip_def.set_position((padding_left, y_def)).set_duration(video.duration)
    
    # Criar composição final
    final_video = CompositeVideoClip([video, clip_word, clip_pos, clip_def])
    
    print(f"Salvando vídeo editado em: {output_path}")
    final_video.write_videofile(
        output_path, 
        codec="libx264", 
        audio_codec="aac",
        fps=video.fps,
        preset="fast"
    )
    
    # Fechar os clips para liberar os arquivos e evitar erros de permissão ao deletar no Windows
    video.close()
    clip_word.close()
    clip_pos.close()
    clip_def.close()
    final_video.close()
    
    print("Processamento concluído.\n")


def fix_encoding(text):
    # Se o texto veio do PowerShell do Windows, ele pode ter sido lido como CP1252 em vez de UTF-8
    try:
        return text.encode('cp1252').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

def main():
    parser = argparse.ArgumentParser(description="Processador de Vídeo: Adiciona blocos de texto estilizados")
    
    # Pastas IO
    parser.add_argument("--input_dir", default="/app/input", help="Diretório de vídeos originais")
    parser.add_argument("--output_dir", default="/app/output", help="Diretório onde os editados serão salvos")
    
    # Tempos de corte
    parser.add_argument("--start_time", default=None, help="Início do corte (ex: 5, 00:00:05)")
    parser.add_argument("--end_time", default=None, help="Fim do corte (ex: 15, 00:00:15)")
    
    # Textos
    parser.add_argument("--word", default="enamored", help="Texto 1 (A Palavra)")
    parser.add_argument("--pos", default="Adjective.", help="Texto 2 (Classe Gramatical)")
    parser.add_argument("--definition", 
                        default="filled with a deep, often gentle or dreamy love; captivated by someone or something with quiet affection", 
                        help="Texto 3 (Definição)")
    
    # Fontes
    parser.add_argument("--font_word", default="/app/fonts/font_word.ttf", help="Caminho da fonte (Texto 1)")
    parser.add_argument("--font_pos", default="/app/fonts/font_pos.ttf", help="Caminho da fonte (Texto 2)")
    parser.add_argument("--font_def", default="/app/fonts/font_def.ttf", help="Caminho da fonte (Texto 3)")
    
    args = parser.parse_args()
    
    # Corrige encoding quebrado pelo terminal do Windows
    args.word = fix_encoding(args.word)
    args.pos = fix_encoding(args.pos)
    args.definition = fix_encoding(args.definition)
    
    # Trata quebras de linha literais (\n) recebidas do terminal/CLI e remove espaços ao redor
    args.word = re.sub(r'\s*\\n\s*', '\n', args.word)
    args.pos = re.sub(r'\s*\\n\s*', '\n', args.pos)
    args.definition = re.sub(r'\s*\\n\s*', '\n', args.definition)
    
    # Cria os diretórios caso não existam
    os.makedirs(args.input_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Varre a pasta de input atrás de formatos compatíveis
    extensions = ["*.mp4", "*.mov", "*.mkv", "*.avi"]
    videos = []
    for ext in extensions:
        videos.extend(glob.glob(os.path.join(args.input_dir, ext)))
        
    if not videos:
        print(f"Nenhum vídeo compatível encontrado em {args.input_dir}")
        return
        
    videos = sorted(videos)

    # Se houver apenas 1 vídeo, verificar se precisa dividir em partes de 20 segundos
    if len(videos) == 1:
        video_path = videos[0]
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            if duration > 20.0:
                print(f"Apenas um vídeo encontrado e sua duração é {duration:.2f}s. Dividindo em subvídeos de 20s...")
                base_name, ext = os.path.splitext(os.path.basename(video_path))
                chunk_length = 20
                num_chunks = int(duration // chunk_length)
                if duration % chunk_length > 0.1: # Evita criar chunks minúsculos no final (menos de 0.1s)
                    num_chunks += 1
                
                new_videos = []
                for i in range(num_chunks):
                    start_cut = i * chunk_length
                    end_cut = min((i + 1) * chunk_length, duration)
                    subclip = clip.subclip(start_cut, end_cut)
                    chunk_name = f"{base_name}_part_{i+1:03d}{ext}"
                    chunk_path = os.path.join(args.input_dir, chunk_name)
                    print(f"Salvando parte {i+1}: {chunk_path}")
                    subclip.write_videofile(
                        chunk_path, 
                        codec="libx264", 
                        audio_codec="aac",
                        fps=clip.fps,
                        preset="fast"
                    )
                    new_videos.append(chunk_path)
                
                clip.close()
                os.remove(video_path)
                print(f"Vídeo original removido: {video_path}")
                videos = sorted(new_videos)
            else:
                clip.close()
        except Exception as e:
            print(f"Erro ao tentar dividir o vídeo: {e}")
            return

    # Processa apenas o PRIMEIRO vídeo
    video_to_process = videos[0]
    _, ext = os.path.splitext(video_to_process)
    safe_word = args.word.replace('\n', '').strip()
    
    # Garante que o nome do arquivo de saída seja seguro (removendo caracteres indesejados)
    safe_word_file = "".join(c for c in safe_word if c.isalnum() or c in " _-")
    output_path = os.path.join(args.output_dir, f"{safe_word_file}{ext}")
    
    process_video(video_to_process, output_path, args)
    
    # Exclui o vídeo original do input após o processamento
    try:
        os.remove(video_to_process)
        print(f"Vídeo processado removido do input: {video_to_process}")
    except Exception as e:
        print(f"Erro ao remover o vídeo do input: {e}")

if __name__ == "__main__":
    main()
