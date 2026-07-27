// In-memory app state. The session drives every permission decision; the rest
// is light caching so screens don't refetch reference data on each render.

export const state = {
  session: null, // {id, username, first_name, role} from GET /api/auth/me
};

export function isAdmin() {
  return state.session?.role === "admin";
}
