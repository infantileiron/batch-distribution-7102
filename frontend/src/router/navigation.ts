export const navigation=[['overview','色样总览'],['datasets','两批原始读数'],['policies','缩放与核宽'],['studies','分布检验任务'],['results','统计与置换证据'],['reviews','迁移复核归档']] as const;
export type Page=typeof navigation[number][0];
