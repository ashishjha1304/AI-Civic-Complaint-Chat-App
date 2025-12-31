# Setup Environment Variables for Vercel Deployment
# Run this script to configure environment variables for your deployed backend

Write-Host "Setting up environment variables for AI Civic Complaint Backend..." -ForegroundColor Green
Write-Host ""

# Change to backend directory
Set-Location backend

Write-Host "Adding SUPABASE_URL..." -ForegroundColor Yellow
$supabaseUrl = Read-Host "Please enter your Supabase project URL (e.g., https://your-project.supabase.co)"
vercel env add SUPABASE_URL production | Out-Null
# Note: In a real script, you'd need to handle the interactive input differently
Write-Host "Please manually run: vercel env add SUPABASE_URL" -ForegroundColor Cyan
Write-Host "And enter: $supabaseUrl" -ForegroundColor White

Write-Host ""
Write-Host "Adding SUPABASE_KEY..." -ForegroundColor Yellow
$supabaseKey = Read-Host "Please enter your Supabase anon key"
Write-Host "Please manually run: vercel env add SUPABASE_KEY" -ForegroundColor Cyan
Write-Host "And enter your Supabase anon key" -ForegroundColor White

Write-Host ""
Write-Host "Adding WEBHOOK_URL (optional)..." -ForegroundColor Yellow
$webhookUrl = Read-Host "Please enter your webhook URL (or press Enter to skip)"
if ($webhookUrl) {
    Write-Host "Please manually run: vercel env add WEBHOOK_URL" -ForegroundColor Cyan
    Write-Host "And enter: $webhookUrl" -ForegroundColor White
}

Write-Host ""
Write-Host "After setting environment variables, redeploy with:" -ForegroundColor Green
Write-Host "cd backend && vercel --prod --yes" -ForegroundColor Cyan

Write-Host ""
Write-Host "✅ Follow the manual steps above to complete environment setup!" -ForegroundColor Green
