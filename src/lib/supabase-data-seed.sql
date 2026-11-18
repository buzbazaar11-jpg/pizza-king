-- ============================================================
-- Pizza King — Comprehensive Data Seed
-- Run in Supabase SQL Editor
-- ============================================================

-- CATEGORIES (7)
INSERT INTO categories (id, title, slug, image_url, sort_order, active) VALUES
  (gen_random_uuid(), 'Pizzas', 'pizzas', 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400', 1, true),
  (gen_random_uuid(), 'Burgers', 'burgers', 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', 2, true),
  (gen_random_uuid(), 'Wraps & Rolls', 'wraps', 'https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400', 3, true),
  (gen_random_uuid(), 'Fried Chicken', 'fried-chicken', 'https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=400', 4, true),
  (gen_random_uuid(), 'Fries & Starters', 'fries', 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400', 5, true),
  (gen_random_uuid(), 'Drinks & Shakes', 'drinks', 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400', 6, true),
  (gen_random_uuid(), 'Deals & Combos', 'deals', 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400', 7, true)
ON CONFLICT (slug) DO NOTHING;

-- FOODS (25 items)
DO $$ DECLARE
  c_pizzas uuid; c_burgers uuid; c_wraps uuid; c_chicken uuid; c_fries uuid; c_drinks uuid;
BEGIN
  SELECT id INTO c_pizzas  FROM categories WHERE slug = 'pizzas'       LIMIT 1;
  SELECT id INTO c_burgers FROM categories WHERE slug = 'burgers'      LIMIT 1;
  SELECT id INTO c_wraps   FROM categories WHERE slug = 'wraps'        LIMIT 1;
  SELECT id INTO c_chicken FROM categories WHERE slug = 'fried-chicken' LIMIT 1;
  SELECT id INTO c_fries   FROM categories WHERE slug = 'fries'        LIMIT 1;
  SELECT id INTO c_drinks  FROM categories WHERE slug = 'drinks'       LIMIT 1;

  INSERT INTO foods (id, title, slug, category_id, description, price, image_url, active) VALUES
    -- Pizzas
    (gen_random_uuid(), 'Malang Special Pizza', 'malang-special-pizza', c_pizzas, 'Our signature pizza loaded with premium toppings', 950, 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400', true),
    (gen_random_uuid(), 'Chicken Tikka Pizza', 'chicken-tikka-pizza', c_pizzas, 'Marinated chicken tikka on a smoky base', 850, 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400', true),
    (gen_random_uuid(), 'BBQ Chicken Pizza', 'bbq-chicken-pizza', c_pizzas, 'Juicy BBQ chicken with bell peppers', 850, 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400', true),
    (gen_random_uuid(), 'Margherita Pizza', 'margherita-pizza', c_pizzas, 'Classic tomato, mozzarella and basil', 650, 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400', true),
    (gen_random_uuid(), 'Peri Peri Pizza', 'peri-peri-pizza', c_pizzas, 'Spicy peri peri sauce with grilled chicken', 900, 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400', true),
    -- Burgers
    (gen_random_uuid(), 'Zinger Burger', 'zinger-burger', c_burgers, 'Crispy spiced chicken fillet in a toasted bun', 350, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', true),
    (gen_random_uuid(), 'Double Zinger Burger', 'double-zinger-burger', c_burgers, 'Double crispy chicken patty with extra sauce', 550, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', true),
    (gen_random_uuid(), 'Crispy Chicken Burger', 'crispy-chicken-burger', c_burgers, 'Light and crispy fried chicken burger', 300, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', true),
    (gen_random_uuid(), 'Beef Smash Burger', 'beef-smash-burger', c_burgers, 'Smashed beef patty with caramelized onions', 450, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', true),
    (gen_random_uuid(), 'Loaded Burger', 'loaded-burger', c_burgers, 'Triple patty, bacon, egg, and all the toppings', 600, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400', true),
    -- Wraps
    (gen_random_uuid(), 'Zinger Wrap', 'zinger-wrap', c_wraps, 'Crispy zinger in a soft tortilla wrap', 320, 'https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400', true),
    (gen_random_uuid(), 'Chicken Tikka Wrap', 'chicken-tikka-wrap', c_wraps, 'Marinated tikka chicken in a grilled wrap', 290, 'https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400', true),
    (gen_random_uuid(), 'Club Wrap', 'club-wrap', c_wraps, 'Chicken, cheese, lettuce and mayo club wrap', 350, 'https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400', true),
    -- Fried Chicken
    (gen_random_uuid(), '3pc Fried Chicken', '3pc-fried-chicken', c_chicken, 'Three pieces of crispy golden fried chicken', 420, 'https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=400', true),
    (gen_random_uuid(), 'Wings 6pc', 'wings-6pc', c_chicken, 'Six crispy hot wings with dipping sauce', 380, 'https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=400', true),
    (gen_random_uuid(), 'Crispy Strips', 'crispy-strips', c_chicken, 'Tender chicken strips with signature seasoning', 290, 'https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=400', true),
    -- Fries
    (gen_random_uuid(), 'Loaded Fries', 'loaded-fries', c_fries, 'Fries topped with cheese, jalapeños and sauce', 250, 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400', true),
    (gen_random_uuid(), 'Regular Fries', 'regular-fries', c_fries, 'Classic golden salted fries', 150, 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400', true),
    (gen_random_uuid(), 'Wedges', 'wedges', c_fries, 'Seasoned thick-cut potato wedges', 200, 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400', true),
    -- Drinks
    (gen_random_uuid(), 'Pepsi 1.5L', 'pepsi-1.5l', c_drinks, 'Chilled Pepsi 1.5 litre bottle', 180, 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400', true),
    (gen_random_uuid(), 'Lahori Lassi', 'lahori-lassi', c_drinks, 'Thick and creamy traditional lassi', 220, 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400', true),
    (gen_random_uuid(), 'Chocolate Shake', 'chocolate-shake', c_drinks, 'Rich thick chocolate milkshake', 280, 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400', true),
    (gen_random_uuid(), 'Mango Shake', 'mango-shake', c_drinks, 'Fresh mango blended milkshake', 260, 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400', true),
    -- 2 more for deals
    (gen_random_uuid(), 'Family Deal', 'family-deal', c_pizzas, '1 Large Pizza + 2 Burgers + 2 Regular Fries + 2 Drinks', 1800, 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400', true),
    (gen_random_uuid(), 'Couple Deal', 'couple-deal', c_pizzas, '1 Medium Pizza + 2 Zinger Burgers + 2 Drinks', 1200, 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400', true)
  ON CONFLICT (slug) DO NOTHING;
END $$;

-- POS TABLES (30)
INSERT INTO pos_tables (table_no, name, seats, area, reserved, active)
SELECT
  n,
  'Table ' || n,
  CASE WHEN n % 3 = 0 THEN 6 WHEN n % 5 = 0 THEN 8 ELSE 4 END,
  CASE WHEN n <= 10 THEN 'Main Hall' WHEN n <= 20 THEN 'Side Section' ELSE 'VIP Area' END,
  false,
  true
FROM generate_series(1, 30) AS n
WHERE NOT EXISTS (SELECT 1 FROM pos_tables WHERE table_no = n);

-- DELIVERY SETTINGS
INSERT INTO delivery_settings (center_name, center_lat, center_lng, free_radius_km, base_delivery_charges)
VALUES ('PWD Islamabad', 33.5651, 73.1486, 3.0, 150)
ON CONFLICT DO NOTHING;

-- DELIVERY AREAS (5 whitelisted zones)
INSERT INTO delivery_areas (name, lat, lng, radius_km, delivery_charge, active) VALUES
  ('Bahria Town Phase 4', 33.5300, 73.2100, 5.0, 250, true),
  ('Soan Gardens',        33.6100, 73.1200, 3.0, 200, true),
  ('Media Town',          33.6300, 73.0800, 4.0, 250, true),
  ('Gulraiz Housing',     33.6500, 73.1500, 3.0, 200, true),
  ('I-8 Islamabad',       33.6961, 73.0551, 8.0, 350, true)
ON CONFLICT DO NOTHING;
