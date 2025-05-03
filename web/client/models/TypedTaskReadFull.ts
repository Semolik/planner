/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TaskReadShort } from './TaskReadShort';
import type { TypedTaskState } from './TypedTaskState';
import type { UserRole } from './UserRole';
export type TypedTaskReadFull = {
    id: string;
    task_type: UserRole;
    description: string;
    link: string;
    for_single_user: boolean;
    task_states: Array<TypedTaskState>;
    due_date?: (string | null);
    parent_task: TaskReadShort;
};

