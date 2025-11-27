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
		port = "8080" // fallback for local runs
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		resp := Health{
			Status:  "ok", // Using "ok" as per mini-service spec (not "healthy")
			Service: "mini-safe",
			Version: "1.0.0",
			Uptime:  time.Since(start).String(),
		}
		if err := json.NewEncoder(w).Encode(resp); err != nil {
			log.Printf("error encoding health response: %v", err)
			http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		}
	})

	log.Printf("[mini-safe] listening on :%s (non-root)", port)
	if err := http.ListenAndServe(":"+port, mux); err != nil {
		log.Fatalf("server error: %v", err)
	}
}
