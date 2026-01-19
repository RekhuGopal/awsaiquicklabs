# -----------------------------
# Prerequisites (set these first)
# -----------------------------
$REGION   = "us-west-2"
$USERNAME = "testuser"
$PASSWORD = "P@ssw0rd123!"

# -----------------------------
# Create Cognito User Pool
# -----------------------------

$Policies = @{
    PasswordPolicy = @{
        MinimumLength = 8
    }
} | ConvertTo-Json -Compress

$policyFile = "$PWD\policies.json"

# Write UTF-8 WITHOUT BOM
[System.IO.File]::WriteAllText($policyFile, $Policies, [System.Text.UTF8Encoding]::new($false))

$poolResponse = aws cognito-idp create-user-pool `
    --pool-name "MyUserPool" `
    --policies file://policies.json `
    --region $REGION | ConvertFrom-Json



$POOL_ID = $poolResponse.UserPool.Id

# -----------------------------
# Create App Client
# -----------------------------
$clientResponse = aws cognito-idp create-user-pool-client `
    --user-pool-id $POOL_ID `
    --client-name "MyClient" `
    --no-generate-secret `
    --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH `
    --region $REGION | ConvertFrom-Json

$CLIENT_ID = $clientResponse.UserPoolClient.ClientId

# -----------------------------
# Create User (Suppress welcome email)
# -----------------------------
aws cognito-idp admin-create-user `
    --user-pool-id $POOL_ID `
    --username $USERNAME `
    --region $REGION `
    --message-action SUPPRESS | Out-Null

# -----------------------------
# Set Permanent Password
# -----------------------------
aws cognito-idp admin-set-user-password `
    --user-pool-id $POOL_ID `
    --username $USERNAME `
    --password $PASSWORD `
    --region $REGION `
    --permanent | Out-Null

# -----------------------------
# Authenticate User
# -----------------------------
$authResponse = aws cognito-idp initiate-auth `
    --client-id $CLIENT_ID `
    --auth-flow USER_PASSWORD_AUTH `
    --auth-parameters "USERNAME=$USERNAME,PASSWORD=$PASSWORD" `
    --region $REGION | ConvertFrom-Json

$BEARER_TOKEN = $authResponse.AuthenticationResult.AccessToken

# -----------------------------
# Output Results
# -----------------------------
Write-Host "Pool ID: $POOL_ID"
Write-Host "Discovery URL: https://cognito-idp.$REGION.amazonaws.com/$POOL_ID/.well-known/openid-configuration"
Write-Host "Client ID: $CLIENT_ID"
Write-Host "Bearer Token: $BEARER_TOKEN"