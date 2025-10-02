FROM rust:1.79 as builder
WORKDIR /app

COPY Cargo.toml .
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release || true

COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/lexcode_core /usr/local/bin/lexcode_core
EXPOSE 8080
CMD ["lexcode_core"]
