import type {Attempt,Run} from '../types/domain';import {Status} from './common/Status';import {format,num} from '../utils/format';
export function AttemptHistory({run,onView,picked}:{run:Run;onView?:(attemptId:string)=>void;picked?:string}){
 const attempts=run.attempts||[];
 if(!attempts.length)return null;
 return <details className="attempt-history" open={Boolean(run.cancel_pending)}><summary>尝试历史 · 当前第 {run.attempt_no} 次 / 共 {attempts.length} 次</summary>
 <p className="muted">每次重试沿用冻结研究的原始批次与口径；撤销原因与旧结果按尝试保留，不覆盖当前记录。</p>
 <div className="table-scroll"><table><thead><tr><th>尝试</th><th>状态</th><th>提交</th><th>结束</th><th>撤销原因 / 错误 / 结果</th><th>结果</th></tr></thead><tbody>
 {attempts.map(a=><tr key={a.id} className={a.current?'current':''}><td>#{a.attempt_no}{a.current?' · 当前':''}</td><td><Status value={a.status}/></td><td>{format(a.created_at)}</td><td>{a.finished_at?format(a.finished_at):'—'}</td><td>{a.cancel_reason?'已撤销：'+a.cancel_reason:a.error||(a.status==='completed'?(a.result_published?'已发布为当前结果':'计算完成，未发布'):'—')}</td><td>{a.result_summary?<button className="link-button" aria-label={`查看尝试 #${a.attempt_no} 的统计`} onClick={()=>onView?.(a.id)}>{picked===a.id?'收起':'查看统计'}</button>:<span className="muted">无</span>}</td></tr>)}
 </tbody></table></div></details>}
