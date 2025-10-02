# syntax=docker/dockerfile:1
FROM rust:1.77 as builder
WORKDIR /usr/src/app

COPY Cargo.toml .
COPY src ./src

RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/src/app/target/release/lexcode_core /usr/local/bin/lexcode_core

EXPOSE 8080
CMD ["lexcode_core"]
