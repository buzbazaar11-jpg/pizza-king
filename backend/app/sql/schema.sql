-- Pizza King standalone schema (mirrors the app's tables)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS categories (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  title text NOT NULL,
  image_url text NOT NULL,
  active boolean DEFAULT true NOT NULL,
  featured boolean DEFAULT true NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS coupon_redemptions (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  coupon_id uuid NOT NULL,
  user_id uuid NOT NULL,
  order_id uuid,
  discount_amount numeric DEFAULT 0 NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS coupons (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  code text NOT NULL,
  description text,
  discount_type text DEFAULT 'percent'::text NOT NULL,
  discount_value numeric DEFAULT 0 NOT NULL,
  min_order_amount numeric DEFAULT 0 NOT NULL,
  max_discount numeric,
  usage_limit integer,
  used_count integer DEFAULT 0 NOT NULL,
  active boolean DEFAULT true NOT NULL,
  expires_at timestamp with time zone,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS deals (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  title text NOT NULL,
  description text,
  price numeric NOT NULL,
  old_price numeric,
  discount_text text DEFAULT 'Hot Deal'::text NOT NULL,
  image_url text NOT NULL,
  badge text DEFAULT 'discount'::text NOT NULL,
  active boolean DEFAULT true NOT NULL,
  featured boolean DEFAULT true NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS delivery_areas (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  name text NOT NULL,
  lat numeric NOT NULL,
  lng numeric NOT NULL,
  radius_km numeric DEFAULT 1 NOT NULL,
  delivery_charges numeric DEFAULT 0 NOT NULL,
  active boolean DEFAULT true NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS delivery_settings (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  center_name text DEFAULT 'PWD Islamabad'::text NOT NULL,
  center_lat numeric DEFAULT 33.5651 NOT NULL,
  center_lng numeric DEFAULT 73.1486 NOT NULL,
  free_radius_km numeric DEFAULT 7 NOT NULL,
  base_delivery_charges numeric DEFAULT 0 NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS foods (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  title text NOT NULL,
  description text,
  price numeric NOT NULL,
  image_url text NOT NULL,
  category_id uuid,
  active boolean DEFAULT true NOT NULL,
  featured boolean DEFAULT false NOT NULL,
  rating numeric DEFAULT 0,
  badge text,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  sku text,
  stock integer
);

CREATE TABLE IF NOT EXISTS loyalty_transactions (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid NOT NULL,
  points integer NOT NULL,
  reason text DEFAULT 'order'::text NOT NULL,
  order_id uuid,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  order_id uuid NOT NULL,
  food_id uuid,
  title text NOT NULL,
  quantity integer DEFAULT 1 NOT NULL,
  price numeric NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid NOT NULL,
  total numeric DEFAULT 0 NOT NULL,
  status text DEFAULT 'pending'::text NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  customer_name text,
  customer_phone text,
  customer_email text,
  customer_address text,
  rider_id uuid,
  coupon_code text,
  discount_amount numeric DEFAULT 0 NOT NULL,
  points_earned integer DEFAULT 0 NOT NULL,
  points_redeemed integer DEFAULT 0 NOT NULL,
  delivery_charges numeric DEFAULT 0 NOT NULL,
  subtotal numeric DEFAULT 0 NOT NULL,
  source text DEFAULT 'web'::text NOT NULL,
  payment_method text DEFAULT 'cod'::text NOT NULL,
  amount_paid numeric DEFAULT 0 NOT NULL,
  order_type text DEFAULT 'delivery'::text NOT NULL,
  table_no text,
  notes text
);

CREATE TABLE IF NOT EXISTS pos_expenses (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  title text NOT NULL,
  amount numeric DEFAULT 0 NOT NULL,
  category text DEFAULT 'general'::text NOT NULL,
  note text,
  created_by uuid,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS pos_shifts (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  cashier_id uuid NOT NULL,
  cashier_name text,
  opening_cash numeric DEFAULT 0 NOT NULL,
  closing_cash numeric,
  expected_cash numeric,
  opened_at timestamp with time zone DEFAULT now() NOT NULL,
  closed_at timestamp with time zone,
  notes text,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS pos_tables (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  table_no integer NOT NULL,
  name text NOT NULL,
  seats integer DEFAULT 4 NOT NULL,
  area text DEFAULT 'Main Hall'::text NOT NULL,
  reserved boolean DEFAULT false NOT NULL,
  active boolean DEFAULT true NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid NOT NULL,
  full_name text,
  phone text,
  address text,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL,
  referral_code text,
  notification_prefs jsonb DEFAULT '{"new_items": false, "promotions": true, "order_updates": true}'::jsonb NOT NULL,
  loyalty_points integer DEFAULT 0 NOT NULL
);

CREATE TABLE IF NOT EXISTS push_tokens (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid NOT NULL,
  token text NOT NULL,
  platform text DEFAULT 'web'::text NOT NULL,
  scope text DEFAULT 'customer'::text NOT NULL,
  user_agent text,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS referrals (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  referrer_id uuid NOT NULL,
  referred_user_id uuid NOT NULL,
  referral_code text NOT NULL,
  reward_granted boolean DEFAULT false NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid NOT NULL,
  user_name text DEFAULT ''::text NOT NULL,
  food_id uuid,
  rating integer DEFAULT 5 NOT NULL,
  comment text DEFAULT ''::text NOT NULL,
  approved boolean DEFAULT false NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS rider_documents (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  rider_id uuid NOT NULL,
  doc_type text NOT NULL,
  file_url text DEFAULT ''::text NOT NULL,
  status text DEFAULT 'pending'::text NOT NULL,
  expiry_date date,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS rider_messages (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  rider_id uuid NOT NULL,
  sender text NOT NULL,
  body text NOT NULL,
  read boolean DEFAULT false NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS rider_notifications (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  rider_id uuid NOT NULL,
  title text NOT NULL,
  body text DEFAULT ''::text NOT NULL,
  read boolean DEFAULT false NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS rider_payouts (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  rider_id uuid NOT NULL,
  amount numeric DEFAULT 0 NOT NULL,
  period_start date,
  period_end date,
  status text DEFAULT 'pending'::text NOT NULL,
  paid_at timestamp with time zone,
  notes text,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS rider_schedule (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  rider_id uuid NOT NULL,
  day_of_week integer NOT NULL,
  start_time text DEFAULT '10:00'::text NOT NULL,
  end_time text DEFAULT '22:00'::text NOT NULL,
  available boolean DEFAULT true NOT NULL
);

CREATE TABLE IF NOT EXISTS rider_settings (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  commission_percent numeric DEFAULT 10 NOT NULL,
  min_payout numeric DEFAULT 1000 NOT NULL,
  support_phone text DEFAULT '+923431497982'::text NOT NULL,
  support_whatsapp text DEFAULT '+923431497982'::text NOT NULL,
  payout_schedule text DEFAULT 'weekly'::text NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS testimonials (
  id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
  name text NOT NULL,
  role text DEFAULT 'Customer'::text,
  avatar text,
  rating integer DEFAULT 5,
  text text NOT NULL,
  is_approved boolean DEFAULT false,
  created_at timestamp without time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_addresses (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid NOT NULL,
  label text DEFAULT 'Home'::text NOT NULL,
  recipient_name text,
  phone text,
  address text NOT NULL,
  lat numeric,
  lng numeric,
  is_default boolean DEFAULT false NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS user_roles (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id uuid NOT NULL,
  role text NOT NULL,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS website_settings (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  restaurant_name text DEFAULT 'AL Maalik Foods'::text NOT NULL,
  contact_email text DEFAULT 'info@almaalikfoods.com'::text NOT NULL,
  contact_phone text DEFAULT '+92 300 1234567'::text NOT NULL,
  address text DEFAULT '123 Food Street, Lahore, Pakistan'::text NOT NULL,
  opening_hours_weekday text DEFAULT '11:00 AM – 11:00 PM'::text NOT NULL,
  opening_hours_weekend text DEFAULT '12:00 PM – 12:00 AM'::text NOT NULL,
  facebook_url text DEFAULT ''::text,
  instagram_url text DEFAULT ''::text,
  twitter_url text DEFAULT ''::text,
  delivery_charges numeric DEFAULT 0 NOT NULL,
  free_delivery_above numeric DEFAULT 0 NOT NULL,
  updated_at timestamp with time zone DEFAULT now() NOT NULL
);

-- ===== standalone additions =====
CREATE TABLE IF NOT EXISTS app_users (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  email text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  full_name text,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);
CREATE TABLE IF NOT EXISTS rider_locations (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  rider_id uuid NOT NULL,
  order_id uuid,
  lat numeric NOT NULL,
  lng numeric NOT NULL,
  accuracy numeric,
  created_at timestamp with time zone DEFAULT now() NOT NULL
);
ALTER TABLE pos_tables ADD COLUMN IF NOT EXISTS code text;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS tracking_token text;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_lat numeric;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivery_lng numeric;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS assigned_at timestamp with time zone;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS delivered_at timestamp with time zone;
ALTER TABLE rider_documents ADD COLUMN IF NOT EXISTS storage_path text;
CREATE UNIQUE INDEX IF NOT EXISTS profiles_user_id_key ON profiles(user_id);
CREATE UNIQUE INDEX IF NOT EXISTS user_roles_user_role_key ON user_roles(user_id, role);
CREATE UNIQUE INDEX IF NOT EXISTS push_tokens_token_key ON push_tokens(token);
CREATE UNIQUE INDEX IF NOT EXISTS coupons_code_key ON coupons(code);
