//! Async PostgreSQL example using `sqlx`.
//!
//! To run this example you need to enable the `sqlx` dependency with the
//! Postgres feature in `Cargo.toml` and execute it inside a Tokio runtime.

use sqlx::{postgres::PgPoolOptions, Row};

pub async fn fetch_version(database_url: &str) -> Result<String, sqlx::Error> {
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(database_url)
        .await?;

    let row = sqlx::query("SELECT version()").fetch_one(&pool).await?;
    Ok(row.try_get::<String, _>(0)?)
}

#[cfg(test)]
mod tests {
    use super::fetch_version;

    #[tokio::test]
    #[ignore = "requires a running PostgreSQL instance"]
    async fn version_query_executes() {
        let url = std::env::var("DATABASE_URL").expect("DATABASE_URL must be set for integration test");
        let version = fetch_version(&url).await.unwrap();
        assert!(version.contains("PostgreSQL"));
    }
}
