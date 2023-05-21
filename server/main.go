package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
)

func serveFileHandler(w http.ResponseWriter, r *http.Request) {
	// Get the filename from the URL path
	fileName := strings.TrimPrefix(r.URL.Path, "/")
	filePath := fmt.Sprintf("./storage/%s", fileName)

	// Check if the file exists
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		http.NotFound(w, r)
		return
	}

	// Serve the file
	http.ServeFile(w, r, filePath)
}

func main() {
	http.HandleFunc("/", serveFileHandler)
	err := http.ListenAndServe(":80", nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
