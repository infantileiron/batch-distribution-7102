export const num=(v:number,d=4)=>Number.isFinite(v)?v.toFixed(d):'不可估计';
export const short=(s:string)=>s.slice(0,12);
export const A_COLOR='#ad5b43',B_COLOR='#68736d';

export const format=(iso:string|null)=>{if(!iso)return '—';const d=new Date(iso);return Number.isNaN(d.getTime())?iso:d.toLocaleString('zh-CN',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'})};
