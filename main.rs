use axum::{
    http::StatusCode,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[derive(Serialize, Deserialize)]
struct Health {
    status: String,
}

#[derive(Serialize, Deserialize)]
struct EmbedRequest {
    text: String,
}

#[derive(Serialize, Deserialize)]
struct EmbedResponse {
    vector: Vec<f32>,
}

#[derive(Serialize, Deserialize)]
struct InferRequest {
    input: String,
}

#[derive(Serialize, Deserialize)]
struct InferMetrics {
    char_count: usize,
    word_count: usize,
    contains_non_ascii: bool,
}

#[derive(Serialize, Deserialize)]
struct InferResponse {
    provider: String,
    model: String,
    response: String,
    metrics: InferMetrics,
}

#[derive(Serialize, Deserialize)]
struct ErrorResponse {
    error: String,
}

async fn health() -> Json<Health> {
    Json(Health {
        status: "ok".to_string(),
    })
}

async fn embed(Json(payload): Json<EmbedRequest>) -> Json<EmbedResponse> {
    let mut v = vec![0f32; 8];
    for (i, b) in payload.text.bytes().enumerate() {
        v[i % 8] += (b as f32) / 255.0;
    }
    Json(EmbedResponse { vector: v })
}

async fn infer(
    Json(payload): Json<InferRequest>,
) -> Result<Json<InferResponse>, (StatusCode, Json<ErrorResponse>)> {
    let trimmed = payload.input.trim();

    if trimmed.is_empty() {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(ErrorResponse {
                error: "input cannot be empty".to_string(),
            }),
        ));
    }

    let char_count = trimmed.chars().count();
    let word_count = trimmed.split_whitespace().count();
    let contains_non_ascii = trimmed.chars().any(|c| !c.is_ascii());

    let response = format!("رد داخلي (Rust): {}", trimmed);

    Ok(Json(InferResponse {
        provider: "lex-rust-internal".to_string(),
        model: "lex-rs-sim-1".to_string(),
        response,
        metrics: InferMetrics {
            char_count,
            word_count,
            contains_non_ascii,
        },
    }))
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
        .route("/embed", post(embed))
        .route("/v1/ai/infer", post(infer));

    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    tracing::info!("LexCode core listening on {}", addr);
    axum::serve(tokio::net::TcpListener::bind(addr).await.unwrap(), app)
        .await
        .unwrap();
}
