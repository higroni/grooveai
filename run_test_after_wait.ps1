# Wait for modules to start
Write-Host "Waiting 15 seconds for modules to fully start..."
Start-Sleep -Seconds 15

# Run the test
Write-Host "`nRunning pipeline test..."
python test_pipeline_modules_1_2_3_4_6_7_8_9_10.py

# Made with Bob
