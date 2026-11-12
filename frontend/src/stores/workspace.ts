import * as datasets from '../api/datasets';import * as policies from '../api/policies';import * as studies from '../api/studies';import * as runs from '../api/runs';import * as reviews from '../api/reviews';import * as reports from '../api/reports';import * as audit from '../api/audit';
export async function loadWorkspace(){const [ds,ps,ss,rs,vs,hs,as]=await Promise.all([datasets.list(),policies.list(),studies.list(),runs.list(),reviews.list(),reports.list(),audit.list()]);return {datasets:ds,policies:ps,studies:ss,runs:rs,reviews:vs,reports:hs,audit:as}}
export type Workspace=Awaited<ReturnType<typeof loadWorkspace>>;
export const empty:Workspace={datasets:[],policies:[],studies:[],runs:[],reviews:[],reports:[],audit:[]};
