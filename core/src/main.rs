use axum::{
    extract::State,
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::{collections::HashMap, net::SocketAddr, sync::Arc};
use tokio::sync::RwLock;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

/* =========================
أنواع البيانات والحالة
========================= */

type Vector = Vec<f32>;
type Store = HashMap<String, Vector>;

#[derive(Clone)]
struct AppState {
    store: Arc<RwLock<Store>>,
}

#[derive(Serialize, Deserialize)]
struct Health {
    status: String,
}

/* ==============
Embedding API
============== */

#[derive(Serialize, Deserialize)]
struct EmbedRequest {
    text: String,
}

#[derive(Serialize, Deserialize)]
struct EmbedResponse {
    vector: Vector,
}

// مولّد متجه بدائي حتى نبدّله لاحقاً بمزوّد فعلي
fn toy_embed(text: &str) -> Vector {
    let mut v = vec![0f32; 8];
    for (i, b) in text.bytes().enumerate() {
        v[i % 8] += (b as f32) / 255.0;
    }
    v
}

async fn health() -> Json<Health> {
    Json(Health {
        status: "ok".to_string(),
    })
}

async fn embed(Json(payload): Json<EmbedRequest>) -> Json<EmbedResponse> {
    Json(EmbedResponse {
        vector: toy_embed(&payload.text),
    })
}

/* ===========================
Index: تخزين المتجهات نصياً
=========================== */

#[derive(Serialize, Deserialize)]
struct IndexItem {
    id: String,
    text: String,
}

#[derive(Serialize, Deserialize)]
struct IndexBulkRequest {
    items: Vec<IndexItem>,
}

#[derive(Serialize, Deserialize)]
struct IndexResponse {
    indexed: usize,
}

async fn index_one(
    State(state): State<AppState>,
    Json(item): Json<IndexItem>,
) -> Json<IndexResponse> {
    let vec = toy_embed(&item.text);
    let mut store = state.store.write().await;
    store.insert(item.id, vec);
    Json(IndexResponse { indexed: 1 })
}

async fn index_bulk(
    State(state): State<AppState>,
    Json(payload): Json<IndexBulkRequest>,
) -> Json<IndexResponse> {
    let mut store = state.store.write().await;
    for it in payload.items {
        let vec = toy_embed(&it.text);
        store.insert(it.id, vec);
    }
    Json(IndexResponse {
        indexed: store.len(),
    })
}

/* ==================
Search: البحث الدلالي
================== */

#[derive(Serialize, Deserialize)]
struct SearchRequest {
    query: String,
    #[serde(default = "default_top_k")]
    top_k: usize,
}

#[derive(Serialize, Deserialize)]
struct SearchHit {
    id: String,
    score: f32,
}

#[derive(Serialize, Deserialize)]
struct SearchResponse {
    hits: Vec<SearchHit>,
}

fn default_top_k() -> usize {
    5
}

fn cosine(a: &Vector, b: &Vector) -> f32 {
    let mut dot = 0f32;
    let mut na = 0f32;
    let mut nb = 0f32;
    for i in 0..a.len().min(b.len()) {
        dot += a[i] * b[i];
        na += a[i] * a[i];
        nb += b[i] * b[i];
    }
    let denom = (na.sqrt() * nb.sqrt()).max(1e-8);
    dot / denom
}

async fn search(
    State(state): State<AppState>,
    Json(req): Json<SearchRequest>,
) -> Json<SearchResponse> {
    let qv = toy_embed(&req.query);
    let store = state.store.read().await;

    let mut scored: Vec<SearchHit> = store
        .iter()
        .map(|(id, v)| SearchHit {
            id: id.clone(),
            score: cosine(&qv, v),
        })
        .collect();

    scored.sort_by(|a, b| {
        b.score
            .partial_cmp(&a.score)
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    scored.truncate(req.top_k);

    Json(SearchResponse { hits: scored })
}

/* ==================
Persistence بسيطة
================== */

const STORE_PATH: &str = "data/store.json";

async fn persist_save(State(state): State<AppState>) -> Json<Health> {
    let store = state.store.read().await;
    let json = serde_json::to_string_pretty(&*store).unwrap_or_else(|_| "{}".to_string());
    std::fs::create_dir_all("data").ok();
    std::fs::write(STORE_PATH, json).ok();
    Json(Health {
        status: "saved".to_string(),
    })
}

async fn persist_load(State(state): State<AppState>) -> Json<Health> {
    match std::fs::read_to_string(STORE_PATH) {
        Ok(s) => {
            if let Ok(map) = serde_json::from_str::<Store>(&s) {
                let mut store = state.store.write().await;
                *store = map;
                Json(Health {
                    status: "loaded".to_string(),
                })
            } else {
                Json(Health {
                    status: "load_error".to_string(),
                })
            }
        }
        Err(_) => Json(Health {
            status: "no_file".to_string(),
        }),
    }
}

/* =========
main()
========= */

#[tokio::main]
async fn main() {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new(
            std::env::var("RUST_LOG").unwrap_or_else(|_| "info".into()),
        ))
        .with(tracing_subscriber::fmt::layer())
        .init();

    let state = AppState {
        store: Arc::new(RwLock::new(HashMap::new())),
    };

    let app = Router::new()
        .route("/health", get(health))
        .route("/embed", post(embed))
        .route("/index", post(index_one))
        .route("/index/bulk", post(index_bulk))
        .route("/search", post(search))
        .route("/persist/save", post(persist_save))
        .route("/persist/load", post(persist_load))
        .with_state(state);

    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    tracing::info!("LexCode core listening on {}", addr);
    axum::serve(tokio::net::TcpListener::bind(addr).await.unwrap(), app)
        .await
        .unwrap();
}
