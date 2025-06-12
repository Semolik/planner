/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TaskRead } from '../models/TaskRead';
import type { UserRole } from '../models/UserRole';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TasksService {
    /**
     * Get Tasks
     * @param page
     * @param hideBusyTasks
     * @param prioritizeUnassigned
     * @param token
     * @returns TaskRead Successful Response
     * @throws ApiError
     */
    public static getTasksTasksGet(
        page: number = 1,
        hideBusyTasks: boolean = true,
        prioritizeUnassigned: boolean = true,
        token?: (string | null),
    ): CancelablePromise<Array<TaskRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tasks',
            headers: {
                'token': token,
            },
            query: {
                'page': page,
                'hide_busy_tasks': hideBusyTasks,
                'prioritize_unassigned': prioritizeUnassigned,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Tasks Token
     * @returns string Successful Response
     * @throws ApiError
     */
    public static getTasksTokenTasksTokenGet(): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tasks/token',
        });
    }
    /**
     * Set Tasks Token
     * @param role
     * @returns string Successful Response
     * @throws ApiError
     */
    public static setTasksTokenTasksTokenPut(
        role: UserRole,
    ): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/tasks/token',
            query: {
                'role': role,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Task By Id
     * @param taskId
     * @returns TaskRead Successful Response
     * @throws ApiError
     */
    public static getTaskByIdTasksTaskIdGet(
        taskId: string,
    ): CancelablePromise<TaskRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tasks/{task_id}',
            path: {
                'task_id': taskId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
