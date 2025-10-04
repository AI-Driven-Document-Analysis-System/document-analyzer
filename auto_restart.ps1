# PowerShell Auto-Restart Script for DocAnalyzer
# This script monitors and restarts the Python process when it crashes

Write-Host "Starting DocAnalyzer with Auto-Restart..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop permanently" -ForegroundColor Yellow

$restartCount = 0

while ($true) {
    try {
        if ($restartCount -gt 0) {
            Write-Host "Restart attempt #$restartCount" -ForegroundColor Cyan
        }
        
        Write-Host "Starting DocAnalyzer server..." -ForegroundColor Green
        
        # Start the Python process
        $process = Start-Process -FilePath "python" -ArgumentList "run.py" -PassThru -NoNewWindow
        
        # Wait for the process to exit
        $process.WaitForExit()
        
        $exitCode = $process.ExitCode
        
        if ($exitCode -eq 0) {
            Write-Host "Server stopped normally (exit code: $exitCode)" -ForegroundColor Green
            break
        } else {
            Write-Host "Server crashed with exit code: $exitCode" -ForegroundColor Red
            $restartCount++
            
            Write-Host "Restarting in 10 seconds... (Press Ctrl+C to stop)" -ForegroundColor Yellow
            
            # Wait 10 seconds with ability to cancel
            for ($i = 10; $i -gt 0; $i--) {
                Write-Host "Restarting in $i seconds..." -ForegroundColor Yellow
                Start-Sleep -Seconds 1
            }
        }
    }
    catch [System.Management.Automation.PipelineStoppedException] {
        Write-Host "Auto-restart stopped by user" -ForegroundColor Red
        break
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Retrying in 10 seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
}

Write-Host "Auto-restart script ended" -ForegroundColor Green
