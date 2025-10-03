@echo off
echo ===================================================
echo MinIO Performance Testing Script
echo ===================================================
echo.

:: Set variables
set MINIO_ALIAS=myminio
set MINIO_URL=http://127.0.0.1:9000
set USERNAME=minioadmin
set PASSWORD=minioadmin
set BUCKET_NAME=testbucket
set TEST_DIR=minio_test_files

:: Create test directory
if not exist %TEST_DIR% mkdir %TEST_DIR%

echo Step 1: Installing MinIO Client (mc)
echo ---------------------------------------------------
:: Download mc client if not exists
if not exist mc.exe (
    echo Downloading MinIO client...
    curl -O https://dl.min.io/client/mc/release/windows-amd64/mc.exe
    if errorlevel 1 (
        echo ERROR: Failed to download mc.exe
        echo Please download manually from: https://dl.min.io/client/mc/release/windows-amd64/mc.exe
        pause
        exit /b 1
    )
) else (
    echo MinIO client already exists
)

echo.
echo Step 2: Configure MinIO Alias
echo ---------------------------------------------------
mc.exe alias set %MINIO_ALIAS% %MINIO_URL% %USERNAME% %PASSWORD%
if errorlevel 1 (
    echo ERROR: Failed to set alias
    pause
    exit /b 1
)

echo.
echo Step 3: Create Test Bucket
echo ---------------------------------------------------
mc.exe mb %MINIO_ALIAS%/%BUCKET_NAME% 2>nul
echo Test bucket created or already exists

echo.
echo Step 4: Generate Test Files
echo ---------------------------------------------------
:: Create different sized test files
echo Generating test files...

:: Small file (1MB)
fsutil file createnew %TEST_DIR%\small_file.dat 1048576 >nul 2>&1

:: Medium file (10MB)
fsutil file createnew %TEST_DIR%\medium_file.dat 10485760 >nul 2>&1

:: Large file (50MB)
fsutil file createnew %TEST_DIR%\large_file.dat 52428800 >nul 2>&1

:: Very large file (100MB)
fsutil file createnew %TEST_DIR%\xlarge_file.dat 104857600 >nul 2>&1

:: Create multiple small files for concurrent testing
for /L %%i in (1,1,10) do (
    fsutil file createnew %TEST_DIR%\file%%i.dat 5242880 >nul 2>&1
)

echo Test files generated successfully!
echo.

echo Step 5: Single File Upload Performance Test
echo ---------------------------------------------------
echo Testing upload speed with 50MB file...
echo Start time: %time%
mc.exe cp %TEST_DIR%\large_file.dat %MINIO_ALIAS%/%BUCKET_NAME%/
echo End time: %time%
echo.

echo Step 6: Single File Download Performance Test
echo ---------------------------------------------------
echo Testing download speed...
echo Start time: %time%
mc.exe cp %MINIO_ALIAS%/%BUCKET_NAME%/large_file.dat %TEST_DIR%\downloaded_large.dat
echo End time: %time%
echo.

echo Step 7: Multiple File Upload Test
echo ---------------------------------------------------
echo Testing upload of different file sizes...
mc.exe cp %TEST_DIR%\small_file.dat %MINIO_ALIAS%/%BUCKET_NAME%/
mc.exe cp %TEST_DIR%\medium_file.dat %MINIO_ALIAS%/%BUCKET_NAME%/
mc.exe cp %TEST_DIR%\xlarge_file.dat %MINIO_ALIAS%/%BUCKET_NAME%/
echo Multiple files uploaded!
echo.

echo Step 8: Concurrent Upload Test
echo ---------------------------------------------------
echo Starting concurrent upload test (10 files)...
echo Start time: %time%

:: Start concurrent uploads
for /L %%i in (1,1,10) do (
    start /B mc.exe cp %TEST_DIR%\file%%i.dat %MINIO_ALIAS%/%BUCKET_NAME%/concurrent/
)

:: Wait for uploads to complete (simple wait)
timeout /t 30 /nobreak >nul

echo End time: %time%
echo Concurrent uploads completed!
echo.

echo Step 9: List Objects Performance Test
echo ---------------------------------------------------
echo Listing all objects in bucket...
mc.exe ls %MINIO_ALIAS%/%BUCKET_NAME% --recursive
echo.

echo Step 10: Detailed Performance Statistics
echo ---------------------------------------------------
echo Getting server statistics...
mc.exe admin info %MINIO_ALIAS%
echo.

echo Step 11: Bandwidth Test with Large File
echo ---------------------------------------------------
echo Testing with 100MB file for accurate throughput measurement...
echo Start time: %time%
mc.exe cp %TEST_DIR%\xlarge_file.dat %MINIO_ALIAS%/%BUCKET_NAME%/performance_test.dat
echo Upload completed at: %time%

echo Starting download test...
echo Start time: %time%
mc.exe cp %MINIO_ALIAS%/%BUCKET_NAME%/performance_test.dat %TEST_DIR%\downloaded_performance.dat
echo Download completed at: %time%
echo.

echo Step 12: Cleanup Test (Optional)
echo ---------------------------------------------------
echo Do you want to cleanup test files? (y/n)
set /p cleanup=
if /i "%cleanup%"=="y" (
    echo Removing test objects from MinIO...
    mc.exe rm %MINIO_ALIAS%/%BUCKET_NAME% --recursive --force
    echo Removing local test files...
    rmdir /s /q %TEST_DIR%
    echo Cleanup completed!
)

echo.
echo ===================================================
echo Performance Testing Completed!
echo ===================================================
echo.
echo Performance Benchmarks to Check:
echo - Upload throughput should be ^> 10MB/s
echo - Download throughput should be ^> 15MB/s
echo - No failed uploads during concurrent operations
echo - Consistent performance across multiple files
echo.
echo Check the timestamps above to calculate actual throughput:
echo Throughput = File Size / Time Taken
echo.
pause