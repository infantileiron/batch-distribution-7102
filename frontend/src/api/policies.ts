import {request} from './client';import type {Policy} from '../types/domain';
export const list=()=>request<Policy[]>('/policies');
export const create=(data:unknown)=>request<Policy>('/policies',data);
