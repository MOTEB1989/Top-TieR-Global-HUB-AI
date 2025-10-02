//! Simple HTTP request example using `reqwest` and `serde`.

use reqwest::Client;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct RateLimit {
    pub resources: serde_json::Value,
}

pub async fn fetch_github_rate_limit() -> Result<RateLimit, reqwest::Error> {
    let client = Client::new();
    let response = client
        .get("https://api.github.com/rate_limit")
        .header("User-Agent", "top-tier-adapter-example")
        .send()
        .await?;

    response.json::<RateLimit>().await
}

#[cfg(test)]
mod tests {
    use super::fetch_github_rate_limit;

    #[tokio::test]
    #[ignore = "requires network access"]
    async fn github_rate_limit_returns_data() {
        let result = fetch_github_rate_limit().await.unwrap();
        assert!(result.resources.is_object());
    }
}
