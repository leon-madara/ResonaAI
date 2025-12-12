#!/bin/bash
# TLS 1.3 Configuration Verification Script
# Verifies that the server is properly configured for TLS 1.3
# 
# Usage: ./verify_tls.sh [hostname] [port]
# Example: ./verify_tls.sh mentalhealth.ke 443

set -e

# Default values
HOSTNAME="${1:-localhost}"
PORT="${2:-443}"
TIMEOUT=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "TLS Configuration Verification Script"
echo "Target: ${HOSTNAME}:${PORT}"
echo "================================================"
echo ""

# Check if openssl is available
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}ERROR: openssl is not installed${NC}"
    exit 1
fi

# Function to check TLS version support
check_tls_version() {
    local version=$1
    local flag=$2
    
    echo -n "Checking ${version} support... "
    
    if echo | timeout ${TIMEOUT} openssl s_client -connect ${HOSTNAME}:${PORT} ${flag} 2>/dev/null | grep -q "Protocol"; then
        echo -e "${GREEN}SUPPORTED${NC}"
        return 0
    else
        echo -e "${YELLOW}NOT SUPPORTED${NC}"
        return 1
    fi
}

# Function to check cipher support
check_cipher() {
    local cipher=$1
    
    echo -n "  Checking cipher: ${cipher}... "
    
    if echo | timeout ${TIMEOUT} openssl s_client -connect ${HOSTNAME}:${PORT} -cipher ${cipher} 2>/dev/null | grep -q "Cipher is"; then
        echo -e "${GREEN}SUPPORTED${NC}"
        return 0
    else
        echo -e "${YELLOW}NOT SUPPORTED${NC}"
        return 1
    fi
}

echo "1. TLS Protocol Version Support"
echo "--------------------------------"

# Check TLS 1.3
echo -n "Checking TLS 1.3 support... "
TLS13_RESULT=$(echo | timeout ${TIMEOUT} openssl s_client -connect ${HOSTNAME}:${PORT} -tls1_3 2>&1 || true)
if echo "${TLS13_RESULT}" | grep -q "TLSv1.3"; then
    echo -e "${GREEN}SUPPORTED (REQUIRED)${NC}"
    TLS13_SUPPORTED=true
else
    echo -e "${RED}NOT SUPPORTED - TLS 1.3 IS REQUIRED${NC}"
    TLS13_SUPPORTED=false
fi

# Check TLS 1.2
echo -n "Checking TLS 1.2 support... "
TLS12_RESULT=$(echo | timeout ${TIMEOUT} openssl s_client -connect ${HOSTNAME}:${PORT} -tls1_2 2>&1 || true)
if echo "${TLS12_RESULT}" | grep -q "TLSv1.2"; then
    echo -e "${GREEN}SUPPORTED (FALLBACK)${NC}"
else
    echo -e "${YELLOW}NOT SUPPORTED${NC}"
fi

# Check that TLS 1.1 is disabled
echo -n "Checking TLS 1.1 is disabled... "
TLS11_RESULT=$(echo | timeout ${TIMEOUT} openssl s_client -connect ${HOSTNAME}:${PORT} -tls1_1 2>&1 || true)
if echo "${TLS11_RESULT}" | grep -q "no protocols available\|wrong version\|handshake failure"; then
    echo -e "${GREEN}DISABLED (CORRECT)${NC}"
else
    echo -e "${RED}ENABLED - SHOULD BE DISABLED${NC}"
fi

# Check that TLS 1.0 is disabled
echo -n "Checking TLS 1.0 is disabled... "
TLS10_RESULT=$(echo | timeout ${TIMEOUT} openssl s_client -connect ${HOSTNAME}:${PORT} -tls1 2>&1 || true)
if echo "${TLS10_RESULT}" | grep -q "no protocols available\|wrong version\|handshake failure"; then
    echo -e "${GREEN}DISABLED (CORRECT)${NC}"
else
    echo -e "${RED}ENABLED - SHOULD BE DISABLED${NC}"
fi

echo ""
echo "2. TLS 1.3 Cipher Suites"
echo "------------------------"

# TLS 1.3 cipher suites
TLS13_CIPHERS=(
    "TLS_AES_256_GCM_SHA384"
    "TLS_CHACHA20_POLY1305_SHA256"
    "TLS_AES_128_GCM_SHA256"
)

for cipher in "${TLS13_CIPHERS[@]}"; do
    echo -n "  ${cipher}... "
    if echo | timeout ${TIMEOUT} openssl s_client -connect ${HOSTNAME}:${PORT} -tls1_3 -ciphersuites ${cipher} 2>/dev/null | grep -q "Cipher is"; then
        echo -e "${GREEN}SUPPORTED${NC}"
    else
        echo -e "${YELLOW}NOT SUPPORTED${NC}"
    fi
done

echo ""
echo "3. Certificate Information"
echo "--------------------------"

CERT_INFO=$(echo | timeout ${TIMEOUT} openssl s_client -connect ${HOSTNAME}:${PORT} -servername ${HOSTNAME} 2>/dev/null | openssl x509 -noout -subject -issuer -dates 2>/dev/null || true)

if [ -n "${CERT_INFO}" ]; then
    echo "${CERT_INFO}"
else
    echo -e "${YELLOW}Could not retrieve certificate information${NC}"
fi

echo ""
echo "4. Security Headers Check"
echo "-------------------------"

if command -v curl &> /dev/null; then
    HEADERS=$(curl -sI https://${HOSTNAME}:${PORT}/ 2>/dev/null || curl -sI http://${HOSTNAME}:${PORT}/ 2>/dev/null || true)
    
    check_header() {
        local header=$1
        local required=$2
        
        echo -n "  ${header}... "
        if echo "${HEADERS}" | grep -qi "^${header}:"; then
            echo -e "${GREEN}PRESENT${NC}"
            return 0
        else
            if [ "${required}" = "required" ]; then
                echo -e "${RED}MISSING (REQUIRED)${NC}"
            else
                echo -e "${YELLOW}MISSING${NC}"
            fi
            return 1
        fi
    }
    
    check_header "Strict-Transport-Security" "required"
    check_header "X-Frame-Options" "required"
    check_header "X-Content-Type-Options" "required"
    check_header "X-XSS-Protection" "recommended"
    check_header "Referrer-Policy" "recommended"
    check_header "Content-Security-Policy" "recommended"
    check_header "Permissions-Policy" "recommended"
else
    echo -e "${YELLOW}curl not available - skipping header check${NC}"
fi

echo ""
echo "5. Forward Secrecy Check"
echo "------------------------"

echo -n "Checking ECDHE support... "
FS_RESULT=$(echo | timeout ${TIMEOUT} openssl s_client -connect ${HOSTNAME}:${PORT} 2>&1 || true)
if echo "${FS_RESULT}" | grep -q "ECDHE"; then
    echo -e "${GREEN}SUPPORTED (PERFECT FORWARD SECRECY)${NC}"
else
    echo -e "${YELLOW}NOT DETECTED${NC}"
fi

echo ""
echo "================================================"
echo "Summary"
echo "================================================"

PASS=true

if [ "${TLS13_SUPPORTED}" = false ]; then
    echo -e "${RED}FAIL: TLS 1.3 is not supported${NC}"
    PASS=false
fi

if [ "${PASS}" = true ]; then
    echo -e "${GREEN}PASS: TLS configuration meets security requirements${NC}"
    exit 0
else
    echo -e "${RED}FAIL: TLS configuration does not meet security requirements${NC}"
    exit 1
fi

