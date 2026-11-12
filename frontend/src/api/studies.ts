import {request} from './client';import type {Study} from '../types/domain';
export const list=()=>request<Study[]>('/studies');
export const create=(data:unknown)=>request<Study>('/studies',data);
