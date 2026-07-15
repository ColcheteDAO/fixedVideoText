FROM python:3.10-slim

# Instalar dependências de sistema essenciais (FFmpeg, ImageMagick e fontes padrão)
RUN apt-get update && \
    apt-get install -y ffmpeg imagemagick fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

# Configuração OBRIGATÓRIA do ImageMagick para funcionamento perfeito do MoviePy
# Por segurança, o ImageMagick bloqueia leituras e escritas de textos temporários (paths).
# Sobrescrevemos o policy.xml com um genérico, liberando recursos, tirando as amarras do "rights=none"
RUN mkdir -p /etc/ImageMagick-6 /etc/ImageMagick-7 && \
    echo '<policymap><policy domain="resource" name="memory" value="2GiB"/><policy domain="resource" name="map" value="4GiB"/><policy domain="resource" name="width" value="16KP"/><policy domain="resource" name="height" value="16KP"/><policy domain="resource" name="area" value="256MB"/><policy domain="resource" name="disk" value="2GiB"/></policymap>' | tee /etc/ImageMagick-6/policy.xml /etc/ImageMagick-7/policy.xml > /dev/null

ENV LANG=C.UTF-8
ENV PYTHONIOENCODING=utf-8

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o script 
COPY main.py .

# Comando padrão
CMD ["python", "main.py"]
