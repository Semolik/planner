/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserRole } from './UserRole';
export type UserCreate = {
    first_name: string;
    last_name: string;
    patronymic?: (string | null);
    vk_id?: (number | null);
    birth_date?: (string | null);
    phone?: (string | null);
    group: string;
    roles?: Array<UserRole>;
    username: string;
    password: string;
    is_active?: (boolean | null);
    is_superuser?: (boolean | null);
    is_verified?: (boolean | null);
    institute_id: string;
};

