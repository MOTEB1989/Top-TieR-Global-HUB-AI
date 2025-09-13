#!/bin/bash

# snap_osint_query.sh - OSINT Query Tool for Top-TieR-Global-HUB-AI
# Quick OSINT data collection and analysis script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
OUTPUT_DIR="${OUTPUT_DIR:-./osint_results}"
VERBOSE="${VERBOSE:-false}"

# Functions
print_usage() {
    cat << EOF
Usage: $0 [OPTIONS] COMMAND [ARGS]

OSINT Query Tool for Top-TieR-Global-HUB-AI

COMMANDS:
    search <query>          Search for OSINT data
    analyze <target>        Analyze target entity
    export <format>         Export results (json|csv|graph)
    status                  Check API server status
    health                  Run health check on all services

OPTIONS:
    -v, --verbose          Enable verbose output
    -o, --output DIR       Set output directory (default: ./osint_results)
    -u, --url URL          Set API base URL (default: http://localhost:8000)
    -h, --help             Show this help message

EXAMPLES:
    $0 status                           # Check API status
    $0 search "domain:example.com"      # Search for domain information
    $0 analyze "192.168.1.1"           # Analyze IP address
    $0 export json                      # Export results as JSON
    $0 health                           # Check all services health

Environment Variables:
    API_BASE_URL     API server base URL
    OUTPUT_DIR       Output directory for results
    VERBOSE          Enable verbose mode (true/false)

EOF
}

log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[${timestamp}] INFO:${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[${timestamp}] WARN:${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[${timestamp}] ERROR:${NC} $message"
            ;;
        "DEBUG")
            if [[ "$VERBOSE" == "true" ]]; then
                echo -e "${BLUE}[${timestamp}] DEBUG:${NC} $message"
            fi
            ;;
    esac
}

check_dependencies() {
    local deps=("curl" "jq")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log "ERROR" "Required dependency '$dep' not found. Please install it."
            exit 1
        fi
    done
}

create_output_dir() {
    if [[ ! -d "$OUTPUT_DIR" ]]; then
        log "INFO" "Creating output directory: $OUTPUT_DIR"
        mkdir -p "$OUTPUT_DIR"
    fi
}

api_request() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    
    log "DEBUG" "Making $method request to $API_BASE_URL$endpoint"
    
    local curl_args=(-s -w "%{http_code}" -H "Content-Type: application/json")
    
    if [[ "$method" == "POST" && -n "$data" ]]; then
        curl_args+=(-d "$data")
    fi
    
    local response
    response=$(curl "${curl_args[@]}" -X "$method" "$API_BASE_URL$endpoint")
    
    local http_code="${response: -3}"
    local body="${response%???}"
    
    if [[ "$http_code" -ge 200 && "$http_code" -lt 300 ]]; then
        echo "$body"
        return 0
    else
        log "ERROR" "API request failed with HTTP $http_code"
        log "ERROR" "Response: $body"
        return 1
    fi
}

cmd_status() {
    log "INFO" "Checking API server status..."
    
    if response=$(api_request "/health"); then
        log "INFO" "API server is running"
        if command -v jq &> /dev/null; then
            echo "$response" | jq .
        else
            echo "$response"
        fi
        return 0
    else
        log "ERROR" "API server is not responding"
        return 1
    fi
}

cmd_search() {
    local query="$1"
    if [[ -z "$query" ]]; then
        log "ERROR" "Search query cannot be empty"
        return 1
    fi
    
    log "INFO" "Searching for: $query"
    
    local search_data
    search_data=$(jq -n --arg q "$query" '{query: $q, type: "osint_search"}')
    
    if response=$(api_request "/api/search" "POST" "$search_data"); then
        local output_file="$OUTPUT_DIR/search_$(date +%Y%m%d_%H%M%S).json"
        echo "$response" > "$output_file"
        log "INFO" "Search results saved to: $output_file"
        
        if command -v jq &> /dev/null; then
            echo "$response" | jq .
        else
            echo "$response"
        fi
    else
        log "ERROR" "Search failed"
        return 1
    fi
}

cmd_analyze() {
    local target="$1"
    if [[ -z "$target" ]]; then
        log "ERROR" "Analysis target cannot be empty"
        return 1
    fi
    
    log "INFO" "Analyzing target: $target"
    
    local analyze_data
    analyze_data=$(jq -n --arg t "$target" '{target: $t, type: "osint_analysis"}')
    
    if response=$(api_request "/api/analyze" "POST" "$analyze_data"); then
        local output_file="$OUTPUT_DIR/analysis_$(date +%Y%m%d_%H%M%S).json"
        echo "$response" > "$output_file"
        log "INFO" "Analysis results saved to: $output_file"
        
        if command -v jq &> /dev/null; then
            echo "$response" | jq .
        else
            echo "$response"
        fi
    else
        log "ERROR" "Analysis failed"
        return 1
    fi
}

cmd_export() {
    local format="${1:-json}"
    
    log "INFO" "Exporting data in $format format..."
    
    local export_data
    export_data=$(jq -n --arg f "$format" '{format: $f}')
    
    if response=$(api_request "/api/export" "POST" "$export_data"); then
        local output_file="$OUTPUT_DIR/export_$(date +%Y%m%d_%H%M%S).$format"
        echo "$response" > "$output_file"
        log "INFO" "Export saved to: $output_file"
        
        if [[ "$format" == "json" ]] && command -v jq &> /dev/null; then
            echo "$response" | jq .
        else
            echo "$response"
        fi
    else
        log "ERROR" "Export failed"
        return 1
    fi
}

cmd_health() {
    log "INFO" "Running comprehensive health check..."
    
    # Check API server
    if cmd_status; then
        log "INFO" "✓ API Server: Healthy"
    else
        log "ERROR" "✗ API Server: Unhealthy"
    fi
    
    # Check if docker-compose services are running
    if command -v docker-compose &> /dev/null; then
        log "INFO" "Checking Docker services..."
        if docker-compose ps | grep -q "Up"; then
            log "INFO" "✓ Docker services are running"
        else
            log "WARN" "⚠ Some Docker services may not be running"
        fi
    fi
    
    # Check database connectivity if available
    if response=$(api_request "/api/db/health" 2>/dev/null); then
        log "INFO" "✓ Database: Connected"
    else
        log "WARN" "⚠ Database: Not available or not configured"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="true"
            shift
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -u|--url)
            API_BASE_URL="$2"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        -*)
            log "ERROR" "Unknown option: $1"
            print_usage
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# Check if command is provided
if [[ $# -eq 0 ]]; then
    log "ERROR" "No command provided"
    print_usage
    exit 1
fi

# Execute command
COMMAND="$1"
shift

# Initialize
check_dependencies
create_output_dir

log "DEBUG" "API Base URL: $API_BASE_URL"
log "DEBUG" "Output Directory: $OUTPUT_DIR"
log "DEBUG" "Command: $COMMAND"

case "$COMMAND" in
    "status")
        cmd_status
        ;;
    "search")
        if [[ $# -eq 0 ]]; then
            log "ERROR" "Search command requires a query argument"
            exit 1
        fi
        cmd_search "$1"
        ;;
    "analyze")
        if [[ $# -eq 0 ]]; then
            log "ERROR" "Analyze command requires a target argument"
            exit 1
        fi
        cmd_analyze "$1"
        ;;
    "export")
        cmd_export "${1:-json}"
        ;;
    "health")
        cmd_health
        ;;
    *)
        log "ERROR" "Unknown command: $COMMAND"
        print_usage
        exit 1
        ;;
esac