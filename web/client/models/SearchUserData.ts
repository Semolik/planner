/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Institute } from './Institute';
/**
 * Данные пользователя в результатах поиска
 */
export type SearchUserData = {
    id: string;
    first_name: string;
    last_name: string;
    group: string;
    institute?: (Institute | null);
};

