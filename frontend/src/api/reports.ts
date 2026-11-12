import {request} from './client';import type {Report} from '../types/domain';
export const list=()=>request<Report[]>('/reports');
export const create=(data:unknown)=>request<Report>('/reports',data);
