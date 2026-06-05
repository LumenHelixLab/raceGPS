Remove-Item -Recurse -Force C:\tmp\edge_debug4 -ErrorAction SilentlyContinue
$p = Start-Process -FilePath 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' -ArgumentList '--user-data-dir=C:\tmp\edge_debug4','--no-first-run','--remote-debugging-port=9222','http://localhost:5173/' -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 8
try {
    $r = Invoke-RestMethod -Uri 'http://localhost:9222/json/list' -UseBasicParsing -TimeoutSec 3
    Write-Host ('count=' + $r.Length)
    foreach ($t in $r) { Write-Host ($t.type + ' ' + $t.url) }
} catch {
    Write-Host 'error' $_
}
