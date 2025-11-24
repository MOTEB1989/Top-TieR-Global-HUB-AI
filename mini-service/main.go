package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"
)

type Health struct {
	Status  string `json:"status"`
	Service string `json:"service"`
	Version string `json:"version"`
	Uptime  string `json:"uptime"`
}

var start = time.Now()

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080" // default local fallback
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		resp := Health{
			Status:  "ok",
			Service: "mini-safe",
			Version: "1.0.0",
			Uptime:  time.Since(start).String(),
		}
		_ = json.NewEncoder(w).Encode(resp)
	})

	log.Printf("[mini-service] listening on :%s (non-root)", port)
	if err := http.ListenAndServe(":"+port, mux); err != nil {
		log.Fatalf("server error: %v", err)
	}
}
