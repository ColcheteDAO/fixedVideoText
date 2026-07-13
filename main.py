import os
import argparse
import glob
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def process_video(input_path, output_path, args):
    print(f"Processando vídeo: {input_path}")
    video = VideoFileClip(input_path)
    
    # Lógica de corte (subclip)
    start = args.start_time if args.start_time else 0
    end = args.end_time if args.end_time else video.duration
    
    if args.start_time or args.end_time:
        video = video.subclip(start, end)
    
    w, h = video.size
    
    # Margens relativas ao tamanho do vídeo (ex: 5% e 8%)
    padding_left = int(w * 0.05)
    padding_bottom = int(h * 0.08)
    max_text_width = int(w * 0.85)
    
    # Tamanhos de fonte proporcionais à altura do vídeo
    fontsize_word = int(h * 0.08)
    fontsize_pos = int(h * 0.04)
    fontsize_def = int(h * 0.035)
    
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

    # Calcular o eixo Y de baixo para cima para alinhar empilhado
    y_def = h - padding_bottom - clip_def.h
    y_pos = y_def - clip_pos.h - int(h * 0.015)
    y_word = y_pos - clip_word.h - int(h * 0.015)
    
    # Aplicar posicionamento e duração (mesma duração do vídeo cortado)
    clip_word = clip_word.set_position((padding_left, y_word)).set_duration(video.duration)
    clip_pos = clip_pos.set_position((padding_left, y_pos)).set_duration(video.duration)
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
    print("Processamento concluído.\n")


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
        
    for video_path in videos:
        filename = os.path.basename(video_path)
        output_path = os.path.join(args.output_dir, f"edited_{filename}")
        process_video(video_path, output_path, args)

if __name__ == "__main__":
    main()
