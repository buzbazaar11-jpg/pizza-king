// The ONLY data connection of the frontend: your FastAPI backend.
// FastAPI (/gateway) forwards to the database configured in backend/.env.
// If FastAPI is stopped, the app has no data.
import { createClient } from "@supabase/supabase-js";
import type { Database } from "@/integrations/supabase/types";

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

// Placeholder only — FastAPI swaps in the real key server-side.
const PUBLIC_PLACEHOLDER = "fastapi-public";

export const supabase = createClient<Database>(`${API_BASE_URL}/gateway`, PUBLIC_PLACEHOLDER, {
  auth: {
    storage: typeof window !== "undefined" ? window.localStorage : undefined,
    storageKey: "pizza-king-auth",
    persistSession: true,
    autoRefreshToken: true,
  },
});
