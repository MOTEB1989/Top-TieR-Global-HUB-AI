use axum::{routing::{get, post}, Router, Json};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[derive(Serialize, Deserialize)]
struct Health { status: String }

#[derive(Serialize, Deserialize)]
struct Ready { ready: bool }

#[derive(Serialize, Deserialize)]
struct EmbedRequest { text: String }

#[derive(Serialize, Deserialize)]
struct EmbedResponse { vector: Vec<f32> }

async fn health() -> Json<Health> {
    Json(Health { status: "ok".to_string() })
}

async fn ready() -> Json<Ready> {
    // In a real system we would check dependencies (DB, cache, upstreams).
    // For now, signal that the service is initialized and ready to receive traffic.
    Json(Ready { ready: true })
}

async fn embed(Json(payload): Json<EmbedRequest>) -> Json<EmbedResponse> {
    let mut v = vec![0f32; 8];
    for (i, b) in payload.text.bytes().enumerate() {
        v[i % 8] += (b as f32) / 255.0;
    }
    Json(EmbedResponse { vector: v })
}

#[tokio::main]
async fn main() {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();

    let app = Router::new()
        .route("/health", get(health))
        .route("/ready", get(ready))
        .route("/embed", post(embed));

    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    tracing::info!("LexCode core listening on {}", addr);
    axum::serve(tokio::net::TcpListener::bind(addr).await.unwrap(), app).await.unwrap();
}
