import {request} from './client';import type {Review} from '../types/domain';
export const list=()=>request<Review[]>('/reviews');
export const create=(data:unknown)=>request<Review>('/reviews',data);
