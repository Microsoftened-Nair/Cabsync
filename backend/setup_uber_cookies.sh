#!/bin/bash
# Quick setup script for Uber cookies

echo "=========================================="
echo "Uber Cookie Setup Helper"
echo "=========================================="
echo ""
echo "Follow these steps:"
echo ""
echo "1. Open Firefox/Chrome and go to: https://m.uber.com"
echo "2. Log in to your Uber account"
echo "3. Search for any ride (enter pickup and dropoff)"
echo "4. Press F12 to open Developer Tools"
echo "5. Go to Network tab"
echo "6. Find the 'graphql' request"
echo "7. Right-click -> Copy -> Copy as cURL"
echo ""
echo "8. Look for the line with: -H 'Cookie: ...'"
echo "9. Copy everything between the quotes after Cookie:"
echo ""
echo "Example:"
echo "  -H 'Cookie: sid=QA.CAESEGc...; csid=1.1765...; jwt-session=eyJhbGc...'"
echo "           ^^^ Copy this part ^^^"
echo ""
echo "10. Paste your cookies below and press Enter:"
echo ""
read -p "Cookies: " cookies

if [ -z "$cookies" ]; then
    echo ""
    echo "❌ No cookies provided. Exiting."
    exit 1
fi

# Save to file
echo "$cookies" > uber_cookies.txt

echo ""
echo "✅ Cookies saved to uber_cookies.txt"
echo ""
echo "Testing connection..."
python3 test_uber_integration.py

echo ""
echo "Done! If you see Uber prices above, the setup is complete!"
