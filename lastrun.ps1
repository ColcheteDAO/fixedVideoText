[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Carregar variáveis do arquivo .env
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim().ToLower()
            $value = $matches[2].Trim()
            if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            Set-Variable -Name $key -Value $value -Scope Script
        }
    }
}

if (-not $word -or -not $pos -or -not $definition) {
    Write-Error "Por favor, defina as variáveis WORD, POS e DEFINITION no arquivo .env"
    exit 1
}
docker run --rm  -v "$(pwd)/input:/app/input" `
-v "$(pwd)/output:/app/output" `
-v "$(pwd)/fonts:/app/fonts" `
processor-video-text python main.py `
--start_time 0 `
--end_time -1  `
--word "$word" `
--pos "$pos" `
--definition "$definition"

# Definir as pastas
$outputDir = "C:\Users\juanc\Videos\tiktok\dicionario"
$destDir = "\\TRUENAS\goldenChest\videos\tiktok\dicionario"
$fileName = "$word.mov"

Move-Item -Path ".\output\$fileName" -Destination $outputDir -Force

# Copiar do output para o diretório de destino na rede
if (Test-Path "$outputDir\$fileName") {
    Copy-Item -Path "$outputDir\$fileName" -Destination $destDir -Force
    Write-Host "Arquivo copiado com sucesso para $destDir"
} else {
    Write-Host "Arquivo $fileName não encontrado em $outputDir"
}