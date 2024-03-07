# PowerShell Script to Set Environment Variables (Example for Public Use)
$env:NOTION_SECRET="your_notion_integration_secret_here"
$env:DATABASE_ID="your_database_id_here"

# Display the environment variables to confirm
Write-Output "NOTION_SECRET: $($env:NOTION_SECRET)"
Write-Output "DATABASE_ID: $($env:DATABASE_ID)"
