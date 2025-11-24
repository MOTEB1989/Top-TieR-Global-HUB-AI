# Multi-stage minimal build
FROM golang:1.22-alpine AS build
WORKDIR /src
RUN adduser -D -u 10001 appuser
COPY go.mod .
COPY main.go .
RUN CGO_ENABLED=0 go build -o /out/mini-server .

FROM scratch
COPY --from=build /etc/passwd /etc/passwd
COPY --from=build /etc/group /etc/group
COPY --from=build /out/mini-server /app/mini-server
USER appuser
ENV PORT=8080
EXPOSE 8080
WORKDIR /app
ENTRYPOINT ["/app/mini-server"]
