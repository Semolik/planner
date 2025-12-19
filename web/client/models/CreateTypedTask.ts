/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserRole } from './UserRole';
export type CreateTypedTask = {
    description: string;
    name: string | null;
    link: string;
    for_single_user: boolean;
    due_date: string;
    task_type: UserRole;
};

