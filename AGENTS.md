## Error handling
- Decode failed rider-creation responses through `getFunctionErrorMessage` and show recoverable errors inside the form; keep server password protections enabled.
- Frontend data access goes only through FastAPI: import `supabase` from `@/lib/backend` (points at `${VITE_API_BASE_URL}/gateway`), never `@/integrations/supabase/client`. Why: the user requires the FastAPI backend to be the sole data path; backend/.env owns the database credentials.
