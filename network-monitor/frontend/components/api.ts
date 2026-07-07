export const API = process.env.BACKEND_URL || 'http://localhost:8000';
export async function api(path:string, init?:RequestInit){const r=await fetch(`${API}${path}`,{...init,cache:'no-store',headers:{'Content-Type':'application/json',...(init?.headers||{})}}); if(!r.ok) throw new Error(await r.text()); return r.status===204?null:r.json();}
