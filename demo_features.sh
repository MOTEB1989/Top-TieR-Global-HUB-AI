#!/bin/bash

# Demo script for testing the new features
# This script demonstrates how to use the new additions

echo "============================================================================"
echo "                    Top-TieR-Global-HUB-AI Feature Demo"
echo "============================================================================"

echo ""
echo "1. Neo4j Initialization"
echo "------------------------"
echo "To initialize Neo4j with OSINT schema, run:"
echo "NEO4J_CID=\$(docker ps --filter 'name=neo4j' -q | head -n1)"
echo "[ -n \"\$NEO4J_CID\" ] && docker exec -i \"\$NEO4J_CID\" cypher-shell -u \"\${NEO4J_USER:-neo4j}\" -p \"\${NEO4J_PASS:-password}\" < db/neo4j/init_graph.cql"

echo ""
echo "2. Mini-Web Service"
echo "-------------------"
echo "To start the mini-web service (private queries), run:"
echo "docker compose --profile mini-web up -d veritas-web"
echo ""
echo "Service will be available at: http://localhost:8088"
echo "API Documentation: http://localhost:8088/docs (when DEBUG=true)"

echo ""
echo "3. Stack Health Check"
echo "----------------------"
echo "To run comprehensive health checks, run:"
echo "./stack_health_check.sh \"your-email@example.com\""

echo ""
echo "4. Manual Testing Commands"
echo "---------------------------"

echo ""
echo "# Check CodeQL workflow syntax:"
echo "yamllint .github/workflows/codeql.yml"

echo ""
echo "# Test Python code compilation:"
echo "python3 -m py_compile veritas-mini-web/app.py"

echo ""
echo "# Start all services including mini-web:"
echo "docker compose --profile mini-web up -d"

echo ""
echo "# Query the mini-web service (requires authentication):"
echo "curl -H \"Authorization: Bearer veritas-mini-token-change-me\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -X POST http://localhost:8088/query \\"
echo "     -d '{\"query\":\"+966500000000\",\"query_type\":\"phone\",\"max_results\":5}'"

echo ""
echo "# Check mini-web service health:"
echo "curl http://localhost:8088/health"

echo ""
echo "# Get system statistics (requires authentication):"
echo "curl -H \"Authorization: Bearer veritas-mini-token-change-me\" \\"
echo "     http://localhost:8088/stats"

echo ""
echo "============================================================================"
echo "                                 Notes"
echo "============================================================================"
echo "- All services are optional and can be enabled individually"
echo "- Change the API_TOKEN in production environments"  
echo "- Neo4j script creates constraints and indexes safely"
echo "- Health check script works with or without running services"
echo "- CodeQL workflow will run automatically on pushes to main"
echo "============================================================================"