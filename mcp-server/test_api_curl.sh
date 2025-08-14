#!/bin/bash

# Load environment variables
source .env

echo "Testing Flex API with curl..."
echo "URL: $FLEX_ENV_URL/users"
echo "Username: $FLEX_ENV_USERNAME"
echo ""

# Create base64 encoded credentials
CREDENTIALS=$(echo -n "$FLEX_ENV_USERNAME:$FLEX_ENV_PASSWORD" | base64)

# Test API call
echo "Making API call..."
curl -v -H "Authorization: Basic $CREDENTIALS" \
     -H "Content-Type: application/vnd.nativ.mio.v1+json" \
     "$FLEX_ENV_URL/users" 2>&1 | grep -E "< HTTP|401|200|{" | head -20