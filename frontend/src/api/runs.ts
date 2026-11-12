import {request} from './client';import type {Run} from '../types/domain';
export const list=()=>request<Run[]>('/runs');
export const create=(data:unknown)=>request<Run>('/runs',data);
export const retry=(id:string)=>request<Run>('/runs/'+id+'/retry',{});
export const cancel=(id:string,reason:string)=>request<Run&{cancel_pending:boolean}>('/runs/'+id+'/cancel',{reason});
