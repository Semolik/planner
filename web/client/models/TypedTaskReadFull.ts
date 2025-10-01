/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TaskReadShort } from './TaskReadShort';
import type { TypedTaskState } from './TypedTaskState';
import type { UserRole } from './UserRole';
export type TypedTaskReadFull = {
    description: string;
    link: string;
    for_single_user: boolean;
    due_date: string;
    task_type: UserRole;
    id: string;
    task_states: Array<TypedTaskState>;
    due_date_passed?: boolean;
    parent_task: TaskReadShort;
};

