-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

-- Create purchases table
CREATE TABLE IF NOT EXISTS purchases (
    id SERIAL PRIMARY KEY,
    supermarket_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    user_id UUID NOT NULL,
    items_list JSONB NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL
);

-- Create indexes for better performance
CREATE INDEX idx_purchases_user_id ON purchases(user_id);
CREATE INDEX idx_purchases_timestamp ON purchases(timestamp);
CREATE INDEX idx_purchases_supermarket_id ON purchases(supermarket_id);

-- Load products data with correct column names
COPY products(name, price) FROM '/docker-entrypoint-initdb.d/data/products_list.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Create temporary table for purchases with correct format
CREATE TEMP TABLE temp_purchases (
    supermarket_id TEXT,
    timestamp TIMESTAMP,
    user_id UUID,
    items_list TEXT,
    total_amount DECIMAL(10, 2)
);

-- Load purchases data
COPY temp_purchases FROM '/docker-entrypoint-initdb.d/data/purchases.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Function to convert items list to JSONB format
CREATE OR REPLACE FUNCTION convert_items_to_jsonb(items_text TEXT, total DECIMAL)
RETURNS JSONB AS $$
DECLARE
    items_array TEXT[];
    item TEXT;
    result JSONB = '[]'::JSONB;
    product_record RECORD;
    item_json JSONB;
BEGIN
    -- Split the items by comma
    items_array := string_to_array(items_text, ',');
    
    -- For each item, create a JSON object
    FOREACH item IN ARRAY items_array LOOP
        -- Look up the product
        SELECT id, name, price INTO product_record 
        FROM products 
        WHERE LOWER(name) = LOWER(TRIM(item));
        
        IF FOUND THEN
            item_json := jsonb_build_object(
                'product_id', product_record.id,
                'name', product_record.name,
                'price', product_record.price,
                'quantity', 1
            );
            result := result || item_json;
        END IF;
    END LOOP;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Convert supermarket_id format and insert into main table
INSERT INTO purchases (supermarket_id, timestamp, user_id, items_list, total_amount)
SELECT 
    CASE 
        WHEN supermarket_id = 'SMKT001' THEN 1
        WHEN supermarket_id = 'SMKT002' THEN 2
        WHEN supermarket_id = 'SMKT003' THEN 3
        ELSE CAST(SUBSTRING(supermarket_id FROM 5) AS INTEGER)
    END as supermarket_id,
    timestamp,
    user_id,
    convert_items_to_jsonb(items_list, total_amount),
    total_amount
FROM temp_purchases;

-- Clean up
DROP TABLE temp_purchases;
DROP FUNCTION convert_items_to_jsonb;