use sha2::{Sha256, Digest};
use chrono::{DateTime, Utc, Duration};

pub struct SecureToken {
    pub hash: String,
    pub repo: String,
    pub expires: DateTime<Utc>,
}

impl SecureToken {
    pub fn new(token: &str, repo: &str) -> Self {
        let mut hasher = Sha256::new();
        hasher.update(token.as_bytes());
        SecureToken {
            hash: format!("{:x}", hasher.finalize()),
            repo: repo.to_string(),
            expires: Utc::now() + Duration::hours(1),
        }
    }
}
