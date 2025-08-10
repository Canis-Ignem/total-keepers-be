#!/bin/bash

# PostgreSQL Database Management Script for Total Keeper

case "$1" in
    start)
        echo "Starting PostgreSQL database..."
        docker-compose up -d postgres
        echo "PostgreSQL is starting. Use 'docker-compose logs postgres' to check logs."
        ;;
    stop)
        echo "Stopping PostgreSQL database..."
        docker-compose stop postgres
        ;;
    restart)
        echo "Restarting PostgreSQL database..."
        docker-compose restart postgres
        ;;
    logs)
        echo "Showing PostgreSQL logs..."
        docker-compose logs -f postgres
        ;;
    connect)
        echo "Connecting to PostgreSQL..."
        docker-compose exec postgres psql -U postgres -d total_keeper_db
        ;;
    reset)
        echo "⚠️  This will delete all data. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "Stopping and removing containers and volumes..."
            docker-compose down -v
            echo "Database reset complete. Run '$0 start' to start fresh."
        else
            echo "Reset cancelled."
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|connect|reset}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the PostgreSQL container"
        echo "  stop    - Stop the PostgreSQL container"
        echo "  restart - Restart the PostgreSQL container"
        echo "  logs    - Show and follow PostgreSQL logs"
        echo "  connect - Connect to PostgreSQL CLI"
        echo "  reset   - Remove all data and containers (DESTRUCTIVE)"
        exit 1
        ;;
esac
