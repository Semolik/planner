/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Institute } from './Institute';
import type { UserRole } from './UserRole';
export type UserReadWithEmail = {
    first_name: string;
    last_name: string;
    patronymic?: (string | null);
    vk_id?: (number | null);
    birth_date?: (string | null);
    phone?: (string | null);
    group: string;
    roles?: Array<UserRole>;
    is_active?: boolean;
    is_superuser: boolean;
    is_verified?: boolean;
    username: string;
    id: string;
    institute: Institute;
    created_at: string;
    updated_at: string;
};

