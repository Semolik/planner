/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Institute } from './Institute';
import type { UserRole } from './UserRole';
export type UserReadShort = {
    id: string;
    first_name: string;
    last_name: string;
    institute: Institute;
    is_active?: boolean;
    roles?: Array<UserRole>;
};

