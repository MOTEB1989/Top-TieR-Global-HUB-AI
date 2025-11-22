FROM rust:1.75-slim as builder
WORKDIR /app
COPY Cargo.toml ./
COPY main.rs ./
RUN mkdir -p src && mv main.rs src/main.rs
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/lexcode_core /usr/local/bin/
EXPOSE 8080
CMD ["lexcode_core"]
