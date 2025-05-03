/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TypedTaskReadFull } from '../models/TypedTaskReadFull';
import type { UpdateTypedTaskState } from '../models/UpdateTypedTaskState';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TypedTasksService {
    /**
     * Update Typed Task State
     * @param typedTaskId
     * @param userId
     * @param requestBody
     * @returns void
     * @throws ApiError
     */
    public static updateTypedTaskStateTasksTypedTasksTypedTaskIdUserUserIdPut(
        typedTaskId: string,
        userId: string,
        requestBody: UpdateTypedTaskState,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'PUT',
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
     * Delete Typed Task State
     * @param typedTaskId
     * @param userId
     * @returns void
     * @throws ApiError
     */
    public static deleteTypedTaskStateTasksTypedTasksTypedTaskIdUserUserIdDelete(
        typedTaskId: string,
        userId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/tasks/typed-tasks/{typed_task_id}/user/{user_id}',
            path: {
                'typed_task_id': typedTaskId,
                'user_id': userId,
            },
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
