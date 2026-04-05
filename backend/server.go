package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"backend/cloudflare"
	"backend/routes"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func main() {
	// Load environment variables from .env file
	if err := godotenv.Load(); err != nil {
		log.Fatal("Error loading .env file")
	}

	// Load and validate environment variables
	config := loadConfig()

	// Initialize MongoDB connection
	mongoClient := initMongoDB(config)
	defer disconnectMongoDB(mongoClient)

	// Initialize Cloudflare R2 client
	r2Client, err := cloudflare.NewR2Client()
	if err != nil {
		log.Fatalf("Failed to initialize Cloudflare R2 client: %v", err)
	}

	// Get database and collections
	db := mongoClient.Database(config.MongoDBName)
	imageCollection := db.Collection(config.ImageCollection)
	projectCollection := db.Collection(config.ProjectCollection)

	// Initialize Gin router
	router := gin.Default()

	// Setup middleware
	setupMiddleware(router, config)

	// Setup all routes
	setupRoutes(router, imageCollection, projectCollection, r2Client)

	// Start server
	log.Printf("Server starting on port %s", config.Port)
	if err := router.Run(config.Port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

// Config holds all environment configuration
type Config struct {
	MongoDBURI        string
	MongoDBName       string
	ImageCollection   string
	ProjectCollection string
	CORSOrigin        string
	Port              string
}

// loadConfig loads and validates all required environment variables
func loadConfig() Config {
	config := Config{
		MongoDBURI:        os.Getenv("MONGODB_URI"),
		MongoDBName:       os.Getenv("MONGODB_DB"),
		ImageCollection:   os.Getenv("IMAGE_COLLECTION"),
		ProjectCollection: os.Getenv("PROJECT_COLLECTION"),
		CORSOrigin:        os.Getenv("CORS_ORIGIN"),
		Port:              os.Getenv("PORT"),
	}

	// Validate all required environment variables
	if err := validateConfig(config); err != nil {
		log.Fatalf("Configuration error: %v", err)
	}

	return config
}

// getEnvOrDefault gets an environment variable or returns a default value
func getEnvOrDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// validateConfig checks that all required environment variables are present
func validateConfig(config Config) error {
	checks := map[string]string{
		"MONGODB_URI":        config.MongoDBURI,
		"MONGODB_DB":         config.MongoDBName,
		"IMAGE_COLLECTION":   config.ImageCollection,
		"PROJECT_COLLECTION": config.ProjectCollection,
		"CORS_ORIGIN":        config.CORSOrigin,
		"PORT":               config.Port,
	}

	for envVar, value := range checks {
		if value == "" {
			return fmt.Errorf("missing required environment variable: %s", envVar)
		}
	}

	return nil
}

// initMongoDB establishes a connection to MongoDB and verifies connectivity
func initMongoDB(config Config) *mongo.Client {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, err := mongo.Connect(ctx, options.Client().ApplyURI(config.MongoDBURI))
	if err != nil {
		log.Fatalf("Failed to create MongoDB client: %v", err)
	}

	// Verify MongoDB connection
	if err := client.Ping(ctx, nil); err != nil {
		log.Fatalf("MongoDB connection failed: %v", err)
	}

	log.Println("MongoDB connected successfully")
	return client
}

// disconnectMongoDB gracefully closes the MongoDB connection
func disconnectMongoDB(client *mongo.Client) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := client.Disconnect(ctx); err != nil {
		log.Fatalf("Failed to disconnect MongoDB: %v", err)
	}

	log.Println("MongoDB disconnected successfully")
}

// setupMiddleware configures all middleware including CORS
func setupMiddleware(router *gin.Engine, config Config) {
	// Configure CORS middleware
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{config.CORSOrigin},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))
}

// setupRoutes registers all application routes
func setupRoutes(router *gin.Engine, imageCollection, projectCollection *mongo.Collection, r2Client *cloudflare.R2Client) {
	// API routes - prefixed with /api
	log.Println("Setting up API routes")
	api := router.Group("/api")
	{
		// Project management routes
		routes.ProjectRoutes(api, projectCollection, imageCollection)

		// Image upload and annotation routes
		routes.ImageRoutes(api, imageCollection, r2Client)

		// Result/annotation retrieval routes
		routes.ResultRoutes(api, imageCollection)
	}
}
