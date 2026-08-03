$ErrorActionPreference = "Continue"
$orig = "C:\Users\liuli\Projects\painting-technique-genealogy\images\originals"
$ua = "PaintingTechniqueGenealogy/1.1 (research; educational rebuild)"

# slug -> list of candidate URLs
$jobs = @{
  "piero-flagellation.jpg" = @(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Flagellation_of_Christ_%28Piero_della_Francesca%29.jpg/2000px-Flagellation_of_Christ_%28Piero_della_Francesca%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/4/4e/Flagellation_of_Christ_%28Piero_della_Francesca%29.jpg"
  )
  "pozzo-sant-ignazio.jpg" = @(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Sant%27Ignazio_%28Rome%29_-_Ceiling.jpg/2000px-Sant%27Ignazio_%28Rome%29_-_Ceiling.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/15/Sant%27Ignazio_%28Rome%29_-_Ceiling.jpg"
  )
  "degas-absinthe.jpg" = @(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Edgar_Degas_-_In_a_Caf%C3%A9_-_Google_Art_Project.jpg/2000px-Edgar_Degas_-_In_a_Caf%C3%A9_-_Google_Art_Project.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/2/20/Edgar_Degas_-_In_a_Caf%C3%A9_-_Google_Art_Project.jpg"
  )
  "leonardo-rocks-london.jpg" = @(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Leonardo_da_Vinci_-_Virgin_of_the_Rocks_-_Google_Art_Project.jpg/1600px-Leonardo_da_Vinci_-_Virgin_of_the_Rocks_-_Google_Art_Project.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/e/eb/Leonardo_da_Vinci_-_Virgin_of_the_Rocks_-_Google_Art_Project.jpg"
  )
  "caravaggio-emmaus.jpg" = @(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/1602-3_Caravaggio%2CSupper_at_Emmaus_National_Gallery%2C_London.jpg/2000px-1602-3_Caravaggio%2CSupper_at_Emmaus_National_Gallery%2C_London.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/9d/1602-3_Caravaggio%2CSupper_at_Emmaus_National_Gallery%2C_London.jpg"
  )
  "reynolds-health-of-the-nation.jpg" = @(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/The_Age_of_Innocence_Reynolds.jpg/1600px-The_Age_of_Innocence_Reynolds.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/c/c5/Sir_Joshua_Reynolds_-_The_Age_of_Innocence_-_Google_Art_Project.jpg"
  )
  "monet-sunrise.jpg" = @(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Claude_Monet%2C_Impression%2C_soleil_levant.jpg/2000px-Claude_Monet%2C_Impression%2C_soleil_levant.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/59/Monet_-_Impression%2C_Sunrise.jpg"
  )
  "constable-hay-wain.jpg" = @(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/John_Constable_The_Hay_Wain.jpg/2000px-John_Constable_The_Hay_Wain.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/d/d0/John_Constable_The_Hay_Wain.jpg"
  )
  "titian-early-hand.jpg" = @(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Tiziano_-_Uomo_col_guanto.jpg/1600px-Tiziano_-_Uomo_col_guanto.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/8/86/Tiziano_-_Uomo_col_guanto.jpg"
  )
  "titian-late-hand.jpg" = @(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Titian_-_Piet%C3%A0_-_WGA22755.jpg/1600px-Titian_-_Piet%C3%A0_-_WGA22755.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/c/c5/Titian_-_Piet%C3%A0_-_WGA22755.jpg"
  )
}

function Test-GoodImage($path) {
  if (-not (Test-Path $path)) { return $false }
  $len = (Get-Item $path).Length
  if ($len -lt 150000) { return $false }
  return $true
}

foreach ($file in $jobs.Keys) {
  $dest = Join-Path $orig $file
  if (Test-GoodImage $dest) {
    Write-Host "[keep] $file ($((Get-Item $dest).Length))"
    continue
  }
  Write-Host "[get] $file"
  $ok = $false
  foreach ($url in $jobs[$file]) {
    Write-Host "  try $url"
    try {
      & curl.exe -L --fail --retry 2 --retry-delay 5 -A $ua -o $dest $url 2>$null
      if (Test-GoodImage $dest) {
        Write-Host "  OK $((Get-Item $dest).Length)"
        $ok = $true
        break
      } else {
        Write-Host "  bad/small"
        if (Test-Path $dest) { Remove-Item $dest -Force }
      }
    } catch {
      Write-Host "  fail $_"
    }
    Start-Sleep -Seconds 8
  }
  if (-not $ok) { Write-Host "  FAILED $file" }
  Start-Sleep -Seconds 12
}
Write-Host "DONE"
