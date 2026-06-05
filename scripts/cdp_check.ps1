Remove-Item -Recurse -Force C:\tmp\edge_debug5 -ErrorAction SilentlyContinue
$edge = Start-Process -FilePath 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' -ArgumentList '--user-data-dir=C:\tmp\edge_debug5','--no-first-run','--remote-debugging-port=9222','http://localhost:5173/' -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 8
$r = Invoke-RestMethod -Uri 'http://localhost:9222/json/list' -UseBasicParsing -TimeoutSec 5
$page = $r | Where-Object { $_.type -eq 'page' -and $_.url -like '*localhost:5173*' } | Select-Object -First 1
if (-not $page) { $page = $r | Where-Object { $_.type -eq 'page' } | Select-Object -First 1 }
if (-not $page) { Write-Error 'no page target'; exit 1 }
Write-Host ('Connecting to ' + $page.webSocketDebuggerUrl)
$ws = New-Object System.Net.WebSockets.ClientWebSocket
$uri = [System.Uri]$page.webSocketDebuggerUrl
$ct = [System.Threading.CancellationToken]::None
$ws.ConnectAsync($uri, $ct).Wait()
function Send($obj) {
    $json = ($obj | ConvertTo-Json -Compress)
    $buf = [System.Text.Encoding]::UTF8.GetBytes($json)
    $seg = New-Object System.ArraySegment[byte] -ArgumentList @(,$buf)
    $ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait()
}
Send @{ id=1; method='Runtime.enable' }
Send @{ id=2; method='Log.enable' }
Send @{ id=3; method='Page.enable' }
Send @{ id=4; method='Page.navigate'; params=@{ url='http://localhost:5173/' } }
Start-Sleep -Seconds 10
Send @{ id=5; method='Runtime.evaluate'; params=@{ expression='JSON.stringify({title: document.title, hasMapCanvas: !!document.querySelector(''.maplibregl-canvas''), hasMapContainer: !!document.getElementById(''map''), bodySnippet: document.body.innerHTML.slice(0,1200)})'; returnByValue=$true } }
$sb = New-Object System.Text.StringBuilder
$timeout = [DateTime]::Now.AddSeconds(15)
while ($ws.State -eq [System.Net.WebSockets.WebSocketState]::Open -and [DateTime]::Now -lt $timeout) {
    $arr = New-Object byte[] 8192
    $seg = New-Object System.ArraySegment[byte] -ArgumentList @(,$arr)
    $task = $ws.ReceiveAsync($seg, $ct)
    if (-not $task.Wait(2000)) { continue }
    $result = $task.Result
    if ($result.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) { break }
    $txt = [System.Text.Encoding]::UTF8.GetString($arr, 0, $result.Count)
    [void]$sb.Append($txt)
    if ($result.EndOfMessage) {
        $msg = $sb.ToString() | ConvertFrom-Json
        $sb.Clear() | Out-Null
        if ($msg.method -in @('Runtime.exceptionThrown','Log.entryAdded')) {
            Write-Host ($msg | ConvertTo-Json -Compress)
        }
        if ($msg.id -eq 5) {
            Write-Host "EVAL_RESULT: $($msg.result.result.value)"
        }
    }
}
try { $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, '', $ct).Wait() } catch {}
Stop-Process -Id $edge.Id -Force -ErrorAction SilentlyContinue
