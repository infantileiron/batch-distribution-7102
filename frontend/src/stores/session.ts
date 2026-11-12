import {request} from '../api/client';
import type {Role} from '../types/domain';
export type User={email:string;role:Role};
export const readUser=():User|null=>{try{return JSON.parse(localStorage.getItem('distribution-user')||'null')}catch{return null}};
export async function login(email:string,password:string){const r=await request<{token:string;user:User}>('/auth/login',{email,password});localStorage.setItem('distribution-token',r.token);localStorage.setItem('distribution-user',JSON.stringify(r.user));return r.user}
export function logout(){localStorage.removeItem('distribution-token');localStorage.removeItem('distribution-user')}
