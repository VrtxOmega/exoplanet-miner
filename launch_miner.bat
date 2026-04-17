@echo off
echo Starting Sovereign Miner Telemetry Backend...
start "Sovereign Telemetry Backend" cmd /c "cd /d c:\Veritas_Lab\exoplanet_miner && python server.py"

echo Starting Sovereign Miner Telemetry Dashboard...
cd /d "c:\Veritas_Lab\exoplanet_miner\dashboard"
npm run dev -- --open
