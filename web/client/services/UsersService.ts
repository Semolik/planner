/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TypedTaskReadFull } from '../models/TypedTaskReadFull';
import type { UserRead } from '../models/UserRead';
import type { UserReadWithEmail } from '../models/UserReadWithEmail';
import type { UserRole } from '../models/UserRole';
import type { UserUpdate } from '../models/UserUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UsersService {
    /**
     * Update User
     * @param userId
     * @param requestBody
     * @returns UserReadWithEmail Successful Response
     * @throws ApiError
     */
    public static updateUserUsersUserIdPut(
        userId: string,
        requestBody: UserUpdate,
    ): CancelablePromise<UserReadWithEmail> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/users/{user_id}',
            path: {
                'user_id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getUserUsersUserIdGet(
        userId: string,
    ): CancelablePromise<(UserReadWithEmail | UserRead)> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete User
     * @param userId
     * @returns void
     * @throws ApiError
     */
    public static deleteUserUsersUserIdDelete(
        userId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/users/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Users:Current User
     * @returns UserReadWithEmail Successful Response
     * @throws ApiError
     */
    public static usersCurrentUserUsersMeGet(): CancelablePromise<UserReadWithEmail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users/me',
        });
    }
    /**
     * Get Users
     * @param search
     * @param page
     * @param orderBy
     * @param order
     * @param superusersToTop
     * @param onlySuperusers
     * @param filterRole
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getUsersUsersGet(
        search?: string,
        page: number = 1,
        orderBy: 'last_name' | 'birth_date' = 'last_name',
        order: 'asc' | 'desc' = 'asc',
        superusersToTop: boolean = false,
        onlySuperusers: boolean = false,
        filterRole?: UserRole,
    ): CancelablePromise<Array<(UserRead | UserReadWithEmail)>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users',
            query: {
                'search': search,
                'page': page,
                'order_by': orderBy,
                'order': order,
                'superusers_to_top': superusersToTop,
                'only_superusers': onlySuperusers,
                'filter_role': filterRole,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User Completed Typed Tasks
     * @param userId
     * @param periodId
     * @returns TypedTaskReadFull Successful Response
     * @throws ApiError
     */
    public static getUserCompletedTypedTasksUsersUserIdTypedTasksCompletedGet(
        userId: string,
        periodId: string,
    ): CancelablePromise<Array<TypedTaskReadFull>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users/{user_id}/typed_tasks/completed',
            path: {
                'user_id': userId,
            },
            query: {
                'period_id': periodId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
