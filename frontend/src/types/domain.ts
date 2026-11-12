export type Role='admin'|'analyst'|'viewer';export type ColorRow={sample_id:string;l:number;a:number;b:number};
export type Dataset={id:string;name:string;source:string;batch_a:ColorRow[];batch_b:ColorRow[];created_at:string};
export type Policy={id:string;name:string;scaling:'none'|'pooled_std';bandwidth:'fixed'|'pooled_median';sigma:number|null;permutations:number;seed:number;created_at:string};
export type Study={id:string;name:string;dataset_id:string;policy_id:string;snapshot:{dataset:Dataset;policy:Policy};created_at:string};
export type Statistic={statistic:number;extreme_count:number;denominator:number;pvalue:number;permutation_statistics:number[]};
export type Result={energy:Statistic;mmd:Statistic;B:number;seed:number;permutations:number[][];sample_sizes:number[];transform:{scaling:string;center:number[];scales:number[];constant_dimensions:number[];bandwidth:string;sigma:number;pooled_median_distance:number;label_independent:boolean};transformed_a:number[][];transformed_b:number[][];raw_a:ColorRow[];raw_b:ColorRow[];summaries:{batch:string;n:number;mean:number[];population_sd:number[]}[];policy:Policy;checksum:string;assumptions:string[];pvalues_adjusted:boolean;comparison:string};
export type Run={id:string;study_id:string;status:'queued'|'running'|'completed'|'failed';result:Result;error:string;created_at:string};
export type Review={id:string;run_id:string;version:number;note:string;decision:'accepted'|'needs_changes';author:string;created_at:string};
export type Report={id:string;run_id:string;review_id:string;title:string;published_by:string;created_at:string};export type Audit={id:string;actor:string;action:string;status:number;created_at:string};
