-- Initialize the database for total-keeper application
-- This script runs automatically when the container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Add some sample goalkeeper gloves data
-- Note: The actual tables will be created by SQLAlchemy migrations

-- Insert sample products (will be executed after SQLAlchemy creates tables)
-- This is commented out as it will be handled by the application
/*
INSERT INTO products (id, name, description, price, img, category, tag, is_active) VALUES
('guante_speed_junior', 'Speed Junior Goalkeeper Gloves', 'Lightweight gloves perfect for junior goalkeepers', 34.99, '/train_with_us/gloves.svg', 'GOALKEEPER_GLOVES', 'JUNIOR', true),
('guante_pro_senior', 'Pro Senior Goalkeeper Gloves', 'Professional grade gloves for experienced goalkeepers', 89.99, '/train_with_us/gloves_pro.svg', 'GOALKEEPER_GLOVES', 'SENIOR', true),
('guante_training', 'Training Goalkeeper Gloves', 'Durable training gloves for daily practice', 45.50, '/train_with_us/gloves_training.svg', 'GOALKEEPER_GLOVES', 'TRAINING', true);

INSERT INTO tags (name, description) VALUES
('junior', 'Products designed for junior players'),
('ligero', 'Lightweight products'),
('profesional', 'Professional grade equipment'),
('entrenamiento', 'Training equipment');

INSERT INTO product_sizes (product_id, size, stock_quantity, is_available) VALUES
('guante_speed_junior', '5', 10, true),
('guante_speed_junior', '6', 15, true),
('guante_speed_junior', '7', 8, true),
('guante_pro_senior', '8', 5, true),
('guante_pro_senior', '9', 12, true),
('guante_pro_senior', '10', 7, true),
('guante_training', '6', 20, true),
('guante_training', '7', 18, true),
('guante_training', '8', 25, true);
*/

-- Log initialization completion
\echo 'Database initialization completed! Tables will be created by SQLAlchemy.';
