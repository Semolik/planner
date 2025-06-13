/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateTypedTaskState } from '../models/CreateTypedTaskState';
import type { TypedTaskReadFull } from '../models/TypedTaskReadFull';
import type { TypedTaskState } from '../models/TypedTaskState';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TypedTasksService {
    /**
     * Assign User To Task
     * @param typedTaskId
     * @param userId
     * @param requestBody
     * @returns TypedTaskState Successful Response
     * @throws ApiError
     */
    public static assignUserToTaskTasksTypedTasksTypedTaskIdUserUserIdPost(
        typedTaskId: string,
        userId: string,
        requestBody: CreateTypedTaskState,
    ): CancelablePromise<TypedTaskState> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/tasks/typed-tasks/{typed_task_id}/user/{user_id}',
            path: {
                'typed_task_id': typedTaskId,
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
     * Get Typed Task
     * @param typedTaskId
     * @returns TypedTaskReadFull Successful Response
     * @throws ApiError
     */
    public static getTypedTaskTasksTypedTasksTypedTaskIdGet(
        typedTaskId: string,
    ): CancelablePromise<TypedTaskReadFull> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tasks/typed-tasks/{typed_task_id}',
            path: {
                'typed_task_id': typedTaskId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
