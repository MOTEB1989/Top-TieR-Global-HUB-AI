//! MongoDB example using the official Rust driver.

use mongodb::{bson::doc, options::ClientOptions, Client, Result};

pub async fn list_database_names(uri: &str) -> Result<Vec<String>> {
    let mut options = ClientOptions::parse(uri).await?;
    options.app_name = Some("TopTierAdapter".into());

    let client = Client::with_options(options)?;
    let names = client.list_database_names(None, None).await?;
    Ok(names)
}

#[cfg(test)]
mod tests {
    use super::list_database_names;

    #[tokio::test]
    #[ignore = "requires a running MongoDB instance"]
    async fn databases_are_listed() {
        let uri = std::env::var("MONGODB_URI").expect("MONGODB_URI must be set for integration test");
        let names = list_database_names(&uri).await.unwrap();
        assert!(!names.is_empty());
    }
}
