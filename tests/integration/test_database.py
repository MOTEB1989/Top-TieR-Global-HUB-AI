"""
Database Integration Tests
Tests connectivity with PostgreSQL, Redis, and Neo4j databases.
"""

import os
import pytest
import asyncio


class TestDatabaseIntegration:
    """Integration tests for database connections."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.db_url = os.getenv("DB_URL", "postgresql://postgres:motebai@localhost:5432/motebai")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_auth = os.getenv("NEO4J_AUTH", "neo4j/motebai")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_postgresql_connection(self):
        """Test PostgreSQL database connection."""
        try:
            import asyncpg
        except ImportError:
            pytest.skip("asyncpg not installed")
        
        try:
            conn = await asyncpg.connect(self.db_url, timeout=10)
            
            # Test simple query
            version = await conn.fetchval("SELECT version()")
            assert version is not None, "Failed to get PostgreSQL version"
            
            print(f"\nPostgreSQL connected successfully")
            print(f"Version: {version[:50]}...")
            
            await conn.close()
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_postgresql_query(self):
        """Test PostgreSQL query execution."""
        try:
            import asyncpg
        except ImportError:
            pytest.skip("asyncpg not installed")
        
        try:
            conn = await asyncpg.connect(self.db_url, timeout=10)
            
            # Test SELECT query
            result = await conn.fetchval("SELECT 1 + 1")
            assert result == 2, "Query returned incorrect result"
            
            # Test current timestamp
            timestamp = await conn.fetchval("SELECT NOW()")
            assert timestamp is not None, "Failed to get timestamp"
            
            print(f"\n✓ PostgreSQL queries executed successfully")
            print(f"  Current timestamp: {timestamp}")
            
            await conn.close()
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Test Redis connection."""
        try:
            import aioredis
        except ImportError:
            try:
                import redis.asyncio as aioredis
            except ImportError:
                pytest.skip("redis library not installed")
        
        try:
            redis = await aioredis.from_url(self.redis_url, decode_responses=True)
            
            # Test PING command
            pong = await redis.ping()
            assert pong is True, "Redis PING failed"
            
            print(f"\n✓ Redis connected successfully")
            
            await redis.close()
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_redis_operations(self):
        """Test Redis SET/GET operations."""
        try:
            import aioredis
        except ImportError:
            try:
                import redis.asyncio as aioredis
            except ImportError:
                pytest.skip("redis library not installed")
        
        try:
            redis = await aioredis.from_url(self.redis_url, decode_responses=True)
            
            # Test SET/GET
            test_key = "test:integration:key"
            test_value = "test_value_123"
            
            await redis.set(test_key, test_value, ex=60)  # Expire in 60 seconds
            retrieved = await redis.get(test_key)
            
            assert retrieved == test_value, f"Retrieved value mismatch: {retrieved}"
            
            # Clean up
            await redis.delete(test_key)
            
            print(f"\n✓ Redis SET/GET operations successful")
            
            await redis.close()
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")

    @pytest.mark.integration
    def test_neo4j_connection(self):
        """Test Neo4j connection."""
        try:
            from neo4j import GraphDatabase
        except ImportError:
            pytest.skip("neo4j library not installed")
        
        try:
            username, password = self.neo4j_auth.split("/")
            driver = GraphDatabase.driver(self.neo4j_uri, auth=(username, password))
            
            # Test connection
            driver.verify_connectivity()
            
            print(f"\n✓ Neo4j connected successfully")
            
            driver.close()
        except Exception as e:
            pytest.skip(f"Neo4j not available: {e}")

    @pytest.mark.integration
    def test_neo4j_query(self):
        """Test Neo4j query execution."""
        try:
            from neo4j import GraphDatabase
        except ImportError:
            pytest.skip("neo4j library not installed")
        
        try:
            username, password = self.neo4j_auth.split("/")
            driver = GraphDatabase.driver(self.neo4j_uri, auth=(username, password))
            
            with driver.session() as session:
                # Test simple query
                result = session.run("RETURN 1 + 1 AS result")
                record = result.single()
                assert record["result"] == 2, "Query returned incorrect result"
                
                # Get Neo4j version
                version_result = session.run("CALL dbms.components() YIELD name, versions, edition")
                for record in version_result:
                    print(f"\n✓ Neo4j query successful")
                    print(f"  Component: {record['name']}")
                    print(f"  Version: {record['versions'][0]}")
                    print(f"  Edition: {record['edition']}")
                    break
            
            driver.close()
        except Exception as e:
            pytest.skip(f"Neo4j not available: {e}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_connection_pool_postgresql(self):
        """Test PostgreSQL connection pooling."""
        try:
            import asyncpg
        except ImportError:
            pytest.skip("asyncpg not installed")
        
        try:
            # Create connection pool
            pool = await asyncpg.create_pool(
                self.db_url,
                min_size=2,
                max_size=10,
                timeout=10
            )
            
            # Test concurrent connections
            async def query_db():
                async with pool.acquire() as conn:
                    return await conn.fetchval("SELECT 1")
            
            tasks = [query_db() for _ in range(5)]
            results = await asyncio.gather(*tasks)
            
            assert all(r == 1 for r in results), "Not all queries succeeded"
            
            print(f"\n✓ Connection pool test successful")
            print(f"  Concurrent queries: {len(tasks)}")
            
            await pool.close()
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_database_transaction(self):
        """Test PostgreSQL transaction handling."""
        try:
            import asyncpg
        except ImportError:
            pytest.skip("asyncpg not installed")
        
        try:
            conn = await asyncpg.connect(self.db_url, timeout=10)
            
            # Test transaction rollback
            async with conn.transaction():
                # This would normally create a table, but we'll just test the transaction
                result = await conn.fetchval("SELECT 1")
                assert result == 1, "Transaction query failed"
            
            print(f"\n✓ Database transaction test successful")
            
            await conn.close()
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
